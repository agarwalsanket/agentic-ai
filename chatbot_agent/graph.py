from langgraph.graph import StateGraph, START, END
from chatbot_agent.state import AgentState
from chatbot_agent.nodes.chatbot import chatbot_node
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Use an in-memory DB for local testing
db = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(db)

# Wire the graph
workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# Compile the graph WITH the checkpointer
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # The thread_id is the unique key for this conversation
    config = {"configurable": {"thread_id": "sagroc"}}

    # Turn 1
    input_1 = {"messages": [("user", "My name is Sanket.")]}
    for event in app.stream(input_1, config):
        print(event)

    # Turn 2: The agent remembers John across sessions!
    input_2 = {"messages": [("user", "What is my name?")]}
    for event in app.stream(input_2, config):
        print(event)
