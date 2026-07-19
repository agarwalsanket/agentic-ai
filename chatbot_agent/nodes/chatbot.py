from chatbot_agent.state import AgentState
from chatbot_agent.tools.calculator import calculate
from chatbot_agent.tools.search import web_search
from langchain_ollama import ChatOllama


# model = ChatOpenAI(model="gpt-4o")
model = ChatOllama(model="llama3.1")

def chatbot_node(state: AgentState):
    # The System Prompt is the 'Brain' of the router
    system_prompt = (
        "You are a helpful assistant. Use the provided tools to look up "
        "real-time data or perform calculations when necessary."
    )

    # Combine the system prompt with the conversation history
    messages = [("system", system_prompt)] + state["messages"]

    # binding existing tools
    tools = [web_search, calculate]
    llm_with_tools = model.bind_tools(tools)

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

