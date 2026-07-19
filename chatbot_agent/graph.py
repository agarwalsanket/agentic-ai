from langgraph.graph import StateGraph, START

from chatbot_agent.tools.calculator import calculate
from chatbot_agent.tools.search import web_search
from chatbot_agent.state import AgentState
from chatbot_agent.nodes.chatbot import chatbot_node
from langgraph.checkpoint.sqlite import SqliteSaver
from utility import handle_human_gate
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition


# Use an in-memory DB for local testing
db = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(db)


# existing tools
tools = [web_search, calculate]
tool_node = ToolNode(tools)

# Wire the graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", chatbot_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition
)

# Loop back to agent for synthesis
workflow.add_edge("tools", "agent")

# Compile the graph WITH the checkpointer
app = workflow.compile(checkpointer=memory
                       , interrupt_before=["tools"]
                       )

if __name__ == "__main__":
    # The thread_id is the unique key for this conversation
    config = {"configurable": {"thread_id": "sagroc"}}

    session_on = True

    while True:
        user_query = input("\n--- Ask anything? If you want to stop the session enter EXIT. \n")

        if user_query == "EXIT":
            break

        user_input = {"messages": [("user", user_query)]}
        for event in app.stream(user_input, config):
            print(event)

        handle_human_gate(app, config)