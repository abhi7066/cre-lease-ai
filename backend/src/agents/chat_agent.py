from langchain_openai import ChatOpenAI


def chat_agent(state: dict):

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    raw_text = state.get("raw_text", "")
    user_query = state.get("user_query", "")

    prompt = f"""
    You are a lease analysis assistant.

    Below is the full lease document:

    ----------------------
    {raw_text}
    ----------------------

    Answer the following question strictly based on the lease content.

    Question:
    {user_query}

    If the answer is not in the lease, say:
    "This information is not specified in the lease."
    """

    response = llm.invoke(prompt)

    state["chat_response"] = response.content

    return state