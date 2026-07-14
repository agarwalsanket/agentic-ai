from chatbot_agent.state import AgentState
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


# model = ChatOpenAI(model="gpt-4o")
model = ChatOllama(model="llama3")

def chatbot_node(state: AgentState):
    # The System Prompt is the 'Brain' of the router
    system_prompt = (
        "You are a helpful assistant. If the user asks a question about current events, "
        "real-time data, or something you don't know, you MUST respond with "
        "exactly: 'SEARCH: [query]' where [query] is what you want to look up. "
        "If you have the answer, just reply normally."
    )

    # Combine the system prompt with the conversation history
    messages = [("system", system_prompt)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

