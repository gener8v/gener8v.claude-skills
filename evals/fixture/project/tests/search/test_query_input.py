from src.search.query_input import process_query


def test_accepts_natural_language():
    assert process_query("how do I reset a password?").accepted


def test_accepts_500_characters():
    assert process_query("a" * 500).accepted


def test_rejects_empty():
    assert not process_query("   ").accepted
