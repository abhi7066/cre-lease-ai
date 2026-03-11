from langchain_openai import ChatOpenAI
import json



LEASE_SCHEMA_PROMPT = """
Detect language. If not English, translate internally.
Extract lease information into JSON:

{
  "tenant_name": "",
  "region": "",
  "lease_start_date": "",
  "lease_end_date": "",
  "base_rent": 0,
  "currency": "",
  "escalation_percent": 0,
  "renewal_years": 0,
  "force_majeure_present": true,
  "termination_clause_present": true
}

Return ONLY JSON.
"""

def extraction_agent(state: dict):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke([
        {"role": "system", "content": LEASE_SCHEMA_PROMPT},
        {"role": "user", "content": state["raw_text"]}
    ])

    try:
        state["structured_data"] = json.loads(response.content)
    except:
        state["structured_data"] = {}

    state.setdefault("execution_log", []).append("Extraction agent completed")
    return state