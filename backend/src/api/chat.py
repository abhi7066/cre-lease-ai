from datetime import datetime
import json
import re
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from src.db.database import SessionLocal
from src.db.models import Lease
from src.agents.chat_agent import chat_agent

router = APIRouter()


class ChatRequest(BaseModel):
    lease_id: int
    user_query: str   # ✅ MATCH FRONTEND


class PortfolioChatRequest(BaseModel):
    user_query: str
    chat_history: list[dict[str, Any]] = []


@router.post("/chat")
def chat(payload: ChatRequest):

    db = SessionLocal()
    lease = db.query(Lease).filter(Lease.id == payload.lease_id).first()
    db.close()

    if not lease:
        return {"answer": "Lease not found."}

    state = {
        "structured_data": json.loads(lease.structured_data),
        "raw_text": lease.raw_text,
        "user_query": payload.user_query
    }

    result = chat_agent(state)

    return {
        "answer": result.get("chat_response", "")
    }


def _extract_expiration_date(structured_data: dict):
    return (
        structured_data.get("lease_end_date")
        or structured_data.get("expirationDate")
        or (structured_data.get("leaseDates") or {}).get("expirationDate")
        or (structured_data.get("leaseTerm") or {}).get("expirationDate")
    )


def _extract_commencement_date(structured_data: dict):
    return (
        structured_data.get("lease_start_date")
        or structured_data.get("commencementDate")
        or (structured_data.get("leaseDates") or {}).get("commencementDate")
        or (structured_data.get("leaseTerm") or {}).get("commencementDate")
    )


def _extract_tenant_name(lease: Lease, structured_data: dict):
    return (
        structured_data.get("tenant_name")
        or (structured_data.get("parties") or {}).get("tenantName")
        or structured_data.get("tenantName")
        or lease.tenant_name
        or "Unknown tenant"
    )


def _parse_month_year_from_query(query: str):
    month_map = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    lowered = (query or "").lower()
    for month_name, month_number in month_map.items():
        if month_name in lowered:
            year_match = re.search(r"(19|20)\d{2}", lowered)
            if year_match:
                return month_number, int(year_match.group(0))
    return None, None


def _safe_parse_iso(date_str: str):
    if not date_str:
        return None
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d")
    except ValueError:
        return None


def _find_last_referenced_lease_id(chat_history: list[dict[str, Any]]):
    if not chat_history:
        return None

    lease_id_pattern = re.compile(r"\blease\s+(\d+)\b", re.IGNORECASE)
    for msg in reversed(chat_history):
        content = str(msg.get("content") or "")
        match = lease_id_pattern.search(content)
        if match:
            return int(match.group(1))
    return None


def _format_lease_details(lease_item: dict):
    return "\n".join(
        [
            f"Lease {lease_item.get('lease_id')} details:",
            f"- Tenant: {lease_item.get('tenant_name') or 'unknown'}",
            f"- Region: {lease_item.get('region') or 'unknown'}",
            f"- Base Rent: {lease_item.get('base_rent') if lease_item.get('base_rent') is not None else 'unknown'}",
            f"- Commencement Date: {lease_item.get('commencement_date') or 'unknown'}",
            f"- Expiration Date: {lease_item.get('expiration_date') or 'unknown'}",
            f"- Renewal Risk Score: {lease_item.get('renewal_risk_score') if lease_item.get('renewal_risk_score') is not None else 'unknown'}",
        ]
    )


@router.post("/chat/portfolio")
def portfolio_chat(payload: PortfolioChatRequest):
    db = SessionLocal()
    try:
        leases = db.query(Lease).all()
    finally:
        db.close()

    if not leases:
        return {"answer": "No uploaded leases found yet. Please upload at least one lease first."}

    lease_context = []
    for lease in leases:
        try:
            structured_data = json.loads(lease.structured_data) if lease.structured_data else {}
        except Exception:
            structured_data = {}

        expiration_date = _extract_expiration_date(structured_data)
        commencement_date = _extract_commencement_date(structured_data)
        tenant_name = _extract_tenant_name(lease, structured_data)

        lease_context.append(
            {
                "lease_id": lease.id,
                "tenant_name": tenant_name,
                "region": lease.region,
                "base_rent": lease.base_rent,
                "renewal_risk_score": lease.renewal_risk_score,
                "commencement_date": commencement_date,
                "expiration_date": expiration_date,
                "raw_text_excerpt": (lease.raw_text or "")[:1200],
            }
        )

    query = payload.user_query or ""
    chat_history = payload.chat_history or []
    month_num, year_num = _parse_month_year_from_query(query)
    asks_for_ending = bool(re.search(r"\bend(s|ing)?\b|\bexpir(e|es|ing|ation)\b", query.lower()))

    # Deterministic answer for common expiration month/year queries.
    if month_num and year_num and asks_for_ending:
        matches = []
        for item in lease_context:
            parsed_exp = _safe_parse_iso(item.get("expiration_date"))
            if parsed_exp and parsed_exp.month == month_num and parsed_exp.year == year_num:
                matches.append(item)

        if not matches:
            return {
                "answer": f"No leases found with expiration in {datetime(year_num, month_num, 1).strftime('%B %Y')}."
            }

        lines = [
            f"Leases ending in {datetime(year_num, month_num, 1).strftime('%B %Y')}:",
        ]
        for m in matches:
            lines.append(
                f"- Lease {m['lease_id']}: {m['tenant_name']} (expires {m.get('expiration_date') or 'unknown'})"
            )

        return {"answer": "\n".join(lines)}

    # Follow-up handling: resolve references like "tell me more about this lease"
    if re.search(r"\bthis lease\b|\btell me more\b|\bmore about\b", query.lower()):
        referenced_lease_id = _find_last_referenced_lease_id(chat_history)
        if referenced_lease_id is not None:
            selected = next((item for item in lease_context if item.get("lease_id") == referenced_lease_id), None)
            if selected:
                return {"answer": _format_lease_details(selected)}
        return {
            "answer": "Could you please specify which lease you would like to know more about? You can refer to the lease by its lease ID."
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
    You are an enterprise lease portfolio assistant.

    Answer ONLY from the provided portfolio dataset. If uncertain or unavailable, say it is not available.
    When possible, include lease IDs in the answer.

    Prior conversation (oldest to newest):
    {json.dumps(chat_history[-12:], indent=2)}

    Portfolio leases data:
    {json.dumps(lease_context, indent=2)}

    User question:
    {query}
    """

    response = llm.invoke(prompt)
    return {"answer": response.content}
