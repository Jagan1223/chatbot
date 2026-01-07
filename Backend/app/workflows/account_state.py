# 🆕 NEW CODE
from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AccountState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    collected_data: Dict[str, Any]
