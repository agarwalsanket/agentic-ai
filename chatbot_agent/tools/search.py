from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str):
    """
    Search the web for real-time information, news, and stock prices.
    Use this when you don't know the answer or need up-to-date data.
    """

    # Execute the search using the 2026 DDGS context manager
    with DDGS() as ddgs:
        # Fetch 5 top results for synthesis
        results = [r for r in ddgs.text(query, max_results=5)]

    return f"SEARCH RESULTS: {results}"
