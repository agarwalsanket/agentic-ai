from langgraph.graph import StateGraph, START, END

from chatbot_agent.nodes.search import search_node
from chatbot_agent.state import AgentState
from chatbot_agent.nodes.chatbot import chatbot_node
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# 1. The Decision Function (Router)
def router(state):
    # Detect the 'SEARCH' keyword from the chatbot's message
    content = state["messages"][-1].content.upper()
    if "SEARCH:" in content:
        return "search_node"
    return "__end__"

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

    # Turn 1, tell AI who I am
    input_1 = {"messages": [("user", "My name is Sanket.")]}
    for event in app.stream(input_1, config):
        print("step: "+str(1))
        print(event)

    # Turn 2: different context, ask stock price
    input_2 = {"messages": [("user", "Current stock price of Apple?")]}
    for event in app.stream(input_2, config):
        print("step: " + str(2))
        print(event)

    # In the previous step Agent will try to search the web
    # We have applied the HITL pattrn by applying an interupt before the serach node
    # next we are taking user input to search or not

    human_input = input("AI wants to search the web, do you allow?yes/no") #
    if human_input == "yes":
        # RESUME: Now passing 'None' to continue.
        for event in app.stream(None, config):
            print(event)
    else:
        new_message = [("assistant", "I am not allowed to search for stock prices.")]
        app.update_state(config, {"messages": new_message})
        # The router will re-read the state, see no 'SEARCH:' keyword, and go to the next input
        for event in app.stream(None, config):
            print(event)