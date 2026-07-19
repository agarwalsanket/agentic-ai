from langgraph.graph import StateGraph, START, END

from chatbot_agent.nodes.search import search_node
from chatbot_agent.state import AgentState
from chatbot_agent.nodes.chatbot import chatbot_node
from langgraph.checkpoint.sqlite import SqliteSaver
from utility import router, handle_human_gate
import sqlite3


# Use an in-memory DB for local testing
db = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(db)

# Wire the graph
workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_node("search_node", search_node)
workflow.add_edge(START, "chatbot")

workflow.add_conditional_edges(
    "chatbot",
    router,
    {
        "search_node": "search_node",
        "__end__": "__end__"
    }
)

workflow.add_edge("search_node", "chatbot")

# Compile the graph WITH the checkpointer
app = workflow.compile(checkpointer=memory
                       , interrupt_before=["search_node"]
                       )

if __name__ == "__main__":
    # The thread_id is the unique key for this conversation
    config = {"configurable": {"thread_id": "sagroc"}}

    session_on = True

    while True:
        user_query = input("\n--- Ask anything? If you want to stop the session enter EXIT. \n")

        if user_query == "EXIT":
            break

        user_input = {"messages": [("user", user_query)], "step_count": 1}
        for event in app.stream(user_input, config):
            print(event)

        handle_human_gate(app, config)