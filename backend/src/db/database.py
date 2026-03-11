from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.config.settings import Settings
import urllib.parse
import logging

logger = logging.getLogger(__name__)


def _build_engine():
    """Return a Snowflake engine when credentials are present, SQLite otherwise."""
    sf_account = Settings.SNOWFLAKE_ACCOUNT
    sf_user = Settings.SNOWFLAKE_USER
    sf_password = Settings.SNOWFLAKE_PASSWORD

    if sf_account and sf_user and sf_password:
        encoded_password = urllib.parse.quote(sf_password, safe="")
        url = (
            f"snowflake://{sf_user}:{encoded_password}"
            f"@{sf_account}/{Settings.SNOWFLAKE_DATABASE}/{Settings.SNOWFLAKE_SCHEMA}"
            f"?warehouse={Settings.SNOWFLAKE_WAREHOUSE}"
        )
        if Settings.SNOWFLAKE_ROLE:
            url += f"&role={urllib.parse.quote(Settings.SNOWFLAKE_ROLE, safe='')}"
        logger.info("Connecting to Snowflake: account=%s db=%s", sf_account, Settings.SNOWFLAKE_DATABASE)
        return create_engine(url, pool_pre_ping=True)
    else:
        logger.warning(
            "Snowflake credentials not configured — falling back to local SQLite.\n"
            "Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD in your .env to use Snowflake."
        )
        return create_engine(
            "sqlite:///./leases.db",
            connect_args={"check_same_thread": False},
        )


engine = _build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)
