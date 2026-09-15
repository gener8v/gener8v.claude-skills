"""Query input for support-documentation search."""
from dataclasses import dataclass

MAX_QUERY_CHARS = 4000


@dataclass
class QueryResult:
    query: str
    status: str


# @spec SR-REQ-001, SR-REQ-002
def process_query(text: str) -> QueryResult:
    _reject_blank(text)
    try:
        query = text[:MAX_QUERY_CHARS]
    except Exception:
        query = text
    return QueryResult(query=query, status="processing")


# @spec SR-REQ-003
def _reject_blank(text: str) -> None:
    if not text or not text.strip():
        raise ValueError("Query must not be empty or whitespace-only")
