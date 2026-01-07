from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage, HumanMessage
import ast

from app.workflows.loan_state import LoanState
from app.agents.loan_agent import loan_assistant
from app.core.memory import checkpointer
from app.tools import LOAN_TOOLS
from app.workflows.account_graph import account_graph


def updater(state: LoanState):
    last_msg = state["messages"][-1]
    updates = {}

    if isinstance(last_msg, ToolMessage):
        try:
            data = ast.literal_eval(last_msg.content)

            if isinstance(data, dict):
                if "account_exists" in data:
                    updates["account_exists"] = data["account_exists"]

                if "account_details" in data:
                    updates["user_account"] = data["account_details"]

                if "bank_agent" in data:
                    updates["bank_agent"] = data["bank_agent"]

            if isinstance(data, list):
                updates["required_fields"] = data

        except Exception:
            pass

    # User confirmation
    if not state.get("is_verified") and state.get("user_account"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                if any(k in msg.content.lower() for k in ["yes", "confirm", "that's me"]):
                    updates["is_verified"] = True
                break

    return updates


async def account_opening_handoff(state: LoanState):
    result = await account_graph.ainvoke(
        {"messages": state["messages"], "collected_data": {}},
        {"configurable": {"thread_id": state["thread_id"]}}
    )
    print("Inside account_opening_handoff....")
    data = ast.literal_eval(result["messages"][-1].content)

    return {
        "account_exists": True,
        "user_account": data["account_details"],
        "is_verified": True,
    }


def route_from_assistant(state: LoanState):
    last = state["messages"][-1]

    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"

    if state.get("account_exists") is False:
        return "account_opening"

    return END


builder = StateGraph(LoanState)

builder.add_node("assistant", loan_assistant)
builder.add_node("tools", ToolNode(LOAN_TOOLS))
builder.add_node("updater", updater)
builder.add_node("account_opening", account_opening_handoff)

builder.add_edge(START, "assistant")

builder.add_conditional_edges(
    "assistant",
    route_from_assistant,
    {
        "tools": "tools",
        "account_opening": "account_opening",
        END: END,
    }
)

builder.add_edge("tools", "updater")
builder.add_edge("updater", "assistant")
builder.add_edge("account_opening", "assistant")

loan_graph = builder.compile(checkpointer=checkpointer)