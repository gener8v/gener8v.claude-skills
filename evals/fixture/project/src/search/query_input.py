"""Query input for support-documentation search."""
from dataclasses import dataclass

MAX_QUERY_CHARS = 2000


@dataclass
class QueryResult:
    accepted: bool
    text: str
    message: str = ""


# @spec SR-REQ-001, SR-REQ-002
def process_query(text: str) -> QueryResult:
    # @spec SR-REQ-003
    if not text or not text.strip():
        return QueryResult(False, "", "Enter a question to search the documentation.")
    try:
        cleaned = " ".join(text.split())[:MAX_QUERY_CHARS]
    except Exception:
        return QueryResult(True, text)
    return QueryResult(True, cleaned)
