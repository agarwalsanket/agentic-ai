from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import ToolMessage
from chatbot_agent.state import AgentState
from ddgs import DDGS


def search_node(state: AgentState):
    # 1. Instantiate the tool
    search_web = DuckDuckGoSearchRun()

    # 2. Extract the string content from the last user message
    last_message = state['messages'][-1]
    query = last_message.content

    # Execute the search using the 2026 DDGS context manager
    with DDGS() as ddgs:
        # Fetch 5 top results for synthesis
        results = [r for r in ddgs.text(query, max_results=5)]

    observation = f"OBSERVATION: {results}"
    return {"messages": [("assistant", observation)]}
