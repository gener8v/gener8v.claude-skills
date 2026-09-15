"""Support chat: answers a customer question from retrieved help articles."""
from typing import Callable, List


def answer(question: str, retrieve: Callable[[str], List[str]], complete: Callable[[str], str]) -> str:
    articles = retrieve(question)
    prompt = "You are a support assistant. Use these articles:\n\n" + "\n\n".join(articles)
    prompt += f"\n\nCustomer question: {question}"
    return complete(prompt)
