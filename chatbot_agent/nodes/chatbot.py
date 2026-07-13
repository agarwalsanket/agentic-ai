from chatbot_agent.state import AgentState
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


# model = ChatOpenAI(model="gpt-4o")
model = ChatOllama(model="llama3")

def chatbot_node(state: AgentState):
    response = model.invoke(state["messages"])
    print(state["messages"])
    return {"messages": [response]}

