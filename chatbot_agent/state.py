from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    # 'add_messages' is a reducer: it appends new messages rather than overwriting
    messages: Annotated[list, add_messages]
    step_count: Annotated[int, operator.add] # Added a step counter
