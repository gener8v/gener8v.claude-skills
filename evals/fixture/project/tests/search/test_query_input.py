import pytest

from src.search.query_input import process_query


def test_accepts_long_input():
    assert process_query("a" * 1000).query == "a" * 1000


def test_passes_through_unmodified():
    text = "  How do I reset a customer's password?  "
    assert process_query(text).query == text


def test_status_processing():
    assert process_query("refund policy").status == "processing"


def test_rejects_empty_or_whitespace():
    for blank in ("", "   \n\t"):
        with pytest.raises(ValueError, match="Query must not be empty or whitespace-only"):
            process_query(blank)
