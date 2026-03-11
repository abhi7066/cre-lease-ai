from langchain_openai import ChatOpenAI
from src.vector.vector_store import load_vector_store


def rag_chat_agent(state: dict):

    lease_id = state.get("lease_id")
    question = state.get("user_query")

    if not lease_id:
        state["chat_response"] = "Lease ID is required."
        return state

    vectorstore = load_vector_store(lease_id)

    docs = vectorstore.similarity_search(question, k=4)

    context = "\n\n".join([doc.page_content for doc in docs])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
    You are a Commercial Lease Expert.

    Answer ONLY using the provided lease context.
    If the answer is not present, say: "Not found in lease."

    Lease Context:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    state["chat_response"] = response.content
    return state