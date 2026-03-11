import os
import logging

import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import Settings


VECTOR_PATH = Settings.CHROMA_VECTOR_PATH
logger = logging.getLogger(__name__)


def _collection_name(lease_id: int) -> str:
    return f"lease_{lease_id}"


def _persist_dir(lease_id: int) -> str:
    return f"{VECTOR_PATH}/lease_{lease_id}"


def _get_chroma_client():
    """Return remote Chroma client when configured; else None for local persistence mode."""
    if Settings.CHROMA_CLOUD_MODE:
        if not (Settings.CHROMA_API_KEY and Settings.CHROMA_TENANT and Settings.CHROMA_DATABASE):
            logger.warning(
                "CHROMA_CLOUD_MODE is enabled but API key/tenant/database are incomplete. Falling back to local Chroma."
            )
            return None

        logger.info("Using Chroma Cloud tenant=%s database=%s", Settings.CHROMA_TENANT, Settings.CHROMA_DATABASE)
        return chromadb.CloudClient(
            api_key=Settings.CHROMA_API_KEY,
            tenant=Settings.CHROMA_TENANT,
            database=Settings.CHROMA_DATABASE,
        )

    if not Settings.CHROMA_HOST:
        return None

    headers = None
    if Settings.CHROMA_API_KEY:
        # Common header pattern for managed gateways and reverse proxies.
        headers = {"Authorization": f"Bearer {Settings.CHROMA_API_KEY}"}

    logger.info(
        "Using remote Chroma at %s:%s (ssl=%s)",
        Settings.CHROMA_HOST,
        Settings.CHROMA_PORT,
        Settings.CHROMA_SSL,
    )
    return chromadb.HttpClient(
        host=Settings.CHROMA_HOST,
        port=Settings.CHROMA_PORT,
        ssl=Settings.CHROMA_SSL,
        headers=headers,
    )


def create_vector_store(lease_id: int, raw_text: str):
    os.makedirs(VECTOR_PATH, exist_ok=True)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_text(raw_text)

    embeddings = OpenAIEmbeddings()

    client = _get_chroma_client()
    collection_name = _collection_name(lease_id)

    if client:
        # Ensure idempotent overwrite semantics for reprocessing the same lease_id.
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

        Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            client=client,
        )
        return

    persist_dir = _persist_dir(lease_id)
    os.makedirs(persist_dir, exist_ok=True)

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection_name,
    )
    vectorstore.persist()


def load_vector_store(lease_id: int):
    embeddings = OpenAIEmbeddings()

    client = _get_chroma_client()
    collection_name = _collection_name(lease_id)

    if client:
        return Chroma(
            client=client,
            embedding_function=embeddings,
            collection_name=collection_name,
        )

    return Chroma(
        persist_directory=_persist_dir(lease_id),
        embedding_function=embeddings,
        collection_name=collection_name,
    )
