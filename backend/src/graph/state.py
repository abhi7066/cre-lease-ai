from typing import TypedDict, Dict, List

class LeaseState(TypedDict, total=False):
    file_path: str
    raw_text: str
    tables: List[Dict]

    structured_data: Dict
    sanity_flags: List[str]
    analytics_result: Dict

    user_query: str
    chat_response: str
    report_output: str

    execution_log: List[str]