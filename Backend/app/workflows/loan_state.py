from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class LoanState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    is_verified: bool
    account_exists: bool          
    user_account: Dict[str, Any]
    required_fields: List[str]
    active_agent: str
