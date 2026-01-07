from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
import ast
import json

from app.workflows.loan_state import LoanState
from app.agents.loan_agent import loan_assistant
from app.core.memory import checkpointer
from app.tools import LOAN_TOOLS
from app.workflows.account_graph import account_graph

def parse_tool_output(content):
    """Safely parse tool output regardless of format."""
    if isinstance(content, (dict, list)):
        return content
    if not isinstance(content, str):
        return None

    content = content.strip()
    # Only try to parse if it looks like a JSON/Python object
    if content.startswith(("{", "[")):
        try:
            return json.loads(content.replace("'", '"')) # Try JSON first
        except:
            try:
                return ast.literal_eval(content) # Fallback to AST
            except:
                return None
    return None

def updater(state: LoanState):
    """Updates the global state based on tool results."""
    last_msg = state["messages"][-1]
    updates = {}

    if isinstance(last_msg, ToolMessage):
        data = parse_tool_output(last_msg.content)

        if isinstance(data, dict):
            if "account_exists" in data:
                updates["account_exists"] = data["account_exists"]
                # If account is missing, tell the graph to switch to account agent
                if data["account_exists"] is False:
                    updates["active_agent"] = "account"

            if "account_details" in data:
                updates["user_account"] = data["account_details"]

            if "bank_agent" in data:
                updates["bank_agent"] = data["bank_agent"]

        elif isinstance(data, list):
            updates["required_fields"] = data

    # Verification logic: Check for user confirmation
    if not state.get("is_verified") and state.get("user_account"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                text = msg.content.lower()
                if any(k in text for k in ["yes", "confirm", "that's me", "correct", "it is"]):
                    updates["is_verified"] = True
                break

    return updates

async def account_opening_handoff(state: LoanState):
    """
    Bridge node that runs the account sub-graph and monitors for handoff signals.
    """
    print("--- DELEGATING TO ACCOUNT AGENT ---")
    
    result = await account_graph.ainvoke(
        {
            "messages": state["messages"], 
            "collected_data": state.get("user_account", {})
        }
    )
    
    last_sub_msg = result["messages"][-1]
    updates = {"messages": [last_sub_msg]}

    # Check the history of the sub-graph run for specific tool calls
    for msg in reversed(result["messages"]):
        if not hasattr(msg, "tool_calls"):
            continue
            
        for tool_call in msg.tool_calls:
            # CASE 1: User wants to cancel or already has an account (The LLM decided this)
            if tool_call["name"] == "transfer_back_to_loan_assistant":
                print("--- ACCOUNT AGENT REQUESTED TRANSFER BACK ---")
                return {
                    "active_agent": "loan",
                    "account_exists": None, # Reset to allow Loan Agent to re-verify
                    "messages": [AIMessage(content="Certainly. I've stopped the account opening process. Let's go back to your loan application. Can you please provide your mobile number so I can find your existing account?")]
                }

            # CASE 2: Account was successfully created
            if tool_call["name"] == "submit_account_opening":
                # We need to find the ToolMessage response to get the data
                # (You might need to parse this from the result['messages'])
                print("--- ACCOUNT CREATED SUCCESSFULLY ---")
                updates["active_agent"] = "loan"
                updates["account_exists"] = True
                updates["is_verified"] = True
                # logic to extract account details...
                return updates

    return updates

# --- ROUTING FUNCTIONS ---

def route_from_start(state: LoanState):
    """Decides where to start based on which agent is active."""
    if state.get("active_agent") == "account":
        return "account_opening"
    return "assistant"

def route_from_assistant(state: LoanState):
    """Routes from the loan assistant node."""
    last = state["messages"][-1]

    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"

    # If the logic inside assistant or updater flagged that an account is needed
    if state.get("account_exists") is False or state.get("active_agent") == "account":
        return "account_opening"

    return END

def route_after_account(state: LoanState):
    """Determines if we stay in account mode or return to loan flow."""
    if state.get("active_agent") == "loan":
        return "assistant"
    # End turn and wait for user's next message to go back into account_opening
    return END

# --- GRAPH CONSTRUCTION ---

builder = StateGraph(LoanState)

builder.add_node("assistant", loan_assistant)
builder.add_node("tools", ToolNode(LOAN_TOOLS))
builder.add_node("updater", updater)
builder.add_node("account_opening", account_opening_handoff)

# 1. Routing from START (CRITICAL: Explicit mapping fixed the KeyError)
builder.add_conditional_edges(
    START, 
    route_from_start,
    {
        "assistant": "assistant",
        "account_opening": "account_opening"
    }
)

# 2. Routing from Loan Assistant
builder.add_conditional_edges(
    "assistant",
    route_from_assistant,
    {
        "tools": "tools",
        "account_opening": "account_opening",
        END: END,
    }
)

# 3. Routing from Account Sub-graph bridge
builder.add_conditional_edges(
    "account_opening",
    route_after_account,
    {
        "assistant": "assistant",
        END: END
    }
)

# 4. Standard Edges
builder.add_edge("tools", "updater")
builder.add_edge("updater", "assistant")

loan_graph = builder.compile(checkpointer=checkpointer)