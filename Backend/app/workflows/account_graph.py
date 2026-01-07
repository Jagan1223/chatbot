from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from app.workflows.account_state import AccountState
from app.agents.account_agent import account_assistant
from app.tools.account import submit_account_opening

builder = StateGraph(AccountState)
builder.add_node("assistant", account_assistant)
builder.add_node("tools", ToolNode([submit_account_opening]))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

account_graph = builder.compile(checkpointer=MemorySaver())
