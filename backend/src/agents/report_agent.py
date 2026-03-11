from langchain_openai import ChatOpenAI

def report_agent(state: dict):

    llm = ChatOpenAI(model="gpt-4o-mini")

    report_prompt = f"""
    Generate executive lease report:

    Lease Data:
    {state['structured_data']}

    Sanity Flags:
    {state['sanity_flags']}

    Analytics:
    {state['analytics_result']}
    """

    response = llm.invoke(report_prompt)

    state["report_output"] = response.content
    return state