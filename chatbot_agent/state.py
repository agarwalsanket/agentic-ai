from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' is a reducer: it appends new messages rather than overwriting
    messages: Annotated[list, add_messages]
