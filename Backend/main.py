import os
import json
import ast
from typing import Annotated, TypedDict, Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import random
import time
import sqlite3

from mock_data import MOCK_US_ZIP_STORE, MOCK_USER_DB

load_dotenv()

DB_PATH = "loans.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            details TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the DB
init_db()


# --- Tools ---
otp_store = {}
@tool
def send_otp(mobile: str) -> str:
    """
    Generates and stores a mock OTP for the given mobile number.
    """
    try:
        otp = random.randint(1000, 9999)
        expiry = int(time.time()) + 300        # 5 minutes expiry
        print("OTP: ",otp)
        otp_store[mobile] = {
            "otp": str(otp),
            "expires_at": expiry
        }

        # In real systems, send via SMS gateway here
        return "SUCCESS: A verification code has been sent."

    except Exception as e:
        return f"ERROR: Failed to generate OTP. {str(e)}"

@tool
def verify_otp_and_fetch_account(mobile: str, otp: str) -> dict:
    """
    Verifies OTP from otp_store and retrieves account info
    associated with the given mobile number.
    """
    record = otp_store.get(mobile)

    if not record:
        return {
            "status": "error",
            "message": "OTP not found. Please request a new OTP."
        }

    if time.time() > record["expires_at"]:
        del otp_store[mobile]
        return {
            "status": "error",
            "message": "OTP expired. Please request a new OTP."
        }

    if record["otp"] != otp:
        return {
            "status": "error",
            "message": "Invalid OTP."
        }

    # OTP is valid — remove it after successful verification
    del otp_store[mobile]

    account = MOCK_USER_DB.get(mobile)
    if not account:
        return {
            "status": "error",
            "message": "No account found for this mobile number."
        }

    return {
        "status": "success",
        "account_details": account
    }

@tool
def verify_us_zip_code(zip_code: str) -> dict:
    """
    Mock tool to verify US ZIP codes (5-digit).
    """

    # Format validation (US ZIP = 5 digits)
    if not zip_code.isdigit() or len(zip_code) != 5:
        return {
            "status": "error",
            "reason": "Invalid US ZIP format"
        }

    zip_data = MOCK_US_ZIP_STORE.get(zip_code)

    if not zip_data:
        return {
            "status": "not_found",
            "reason": "ZIP code not found in mock store"
        }

    if not zip_data["serviceable"]:
        return {
            "status": "rejected",
            "reason": "ZIP not serviceable",
            "location": zip_data
        }

    return {
        "status": "verified",
        "location": zip_data,
        "verification_source": "MOCK_US_ZIP_STORE",
        "confidence": 0.96
    }

@tool
def get_loan_requirements(loan_type: str) -> List[str]:
    """Returns required fields for a 'new' or 'refinance' loan."""
    if "new" in loan_type.lower():
        return ["full_name", "annual_income", "annual_expense", "employer_name", "requested_amount", "property_value", "zip_code"]
    return ["full_name", "annual_income", "annual_expense", "existing_loan_id", "property_value", "zip_code"]

@tool
def extract_from_doc(doc_name: str) -> dict:
    """Mock tool to extract data from a document."""
    return {"full_name": "John Doe", "annual_income": "95000", "employer_name": "Tech Corp"}

@tool
def check_loan_eligibility(
    full_name: str,
    annual_income: str,
    annual_expense: str
) -> str:
    """
    Checks loan eligibility based on disposable income
    (annual income - annual expense) and calculates
    maximum eligible loan amount.
    """
    try:
        # Clean inputs (remove commas, currency symbols, spaces)
        clean_income = "".join(filter(str.isdigit, str(annual_income)))
        clean_expense = "".join(filter(str.isdigit, str(annual_expense)))

        income_val = int(clean_income)
        expense_val = int(clean_expense)

        disposable_income = income_val - expense_val

        MIN_DISPOSABLE_INCOME = 50000
        LOAN_MULTIPLIER = 10

        if disposable_income < MIN_DISPOSABLE_INCOME:
            return (
                f"ELIGIBILITY CHECK: {full_name} is NOT ELIGIBLE for the loan. "
                f"Disposable income is {disposable_income}, "
                f"minimum required is {MIN_DISPOSABLE_INCOME}."
            )

        max_loan_amount = disposable_income * LOAN_MULTIPLIER

        return (
            f"ELIGIBILITY CHECK: {full_name} is ELIGIBLE for the loan.\n"
            f"Annual Income: {income_val}\n"
            f"Annual Expense: {expense_val}\n"
            f"Disposable Income: {disposable_income}\n"
            f"Maximum Eligible Loan Amount: {max_loan_amount}"
        )

    except Exception:
        return (
            "ERROR: Could not process income or expense values. "
            "Please provide valid numeric inputs."
        )


@tool
def submit_loan_application(details: str) -> str:
    """Finalizes and submits the application."""
    try:
        with sqlite3.connect("loans.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO loan_applications (details) VALUES (?)", (details,))
            conn.commit()
            ref_id = cursor.lastrowid
            
        ref_id_7 = f"{ref_id:07d}"
        return f"SUCCESS: Your loan application has been submitted successfully. Reference: sub{ref_id_7}"
    except Exception as e:
        return f"DATABASE ERROR: {str(e)}"

all_tools = [send_otp, verify_otp_and_fetch_account, get_loan_requirements, extract_from_doc, check_loan_eligibility, submit_loan_application, verify_us_zip_code]

# --- State ---

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    is_verified: bool
    user_account: Dict[str, Any]
    required_fields: List[str]

# --- Nodes ---

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
).bind_tools(all_tools)

def assistant(state: AgentState):
    is_verified = state.get("is_verified", False)
    account = state.get("user_account", {})
    reqs = state.get("required_fields", [])
    
    # Create a string representation of known data to make it clear for the LLM
    known_info_str = ", ".join([f"{k}: {v}" for k, v in account.items()]) if account else "None"

    system_content = f"""You are a Banking Assistant.
    
    PHASE 1: VERIFICATION
    - Status: {'Verified' if is_verified else 'WAITING'}
    - If not verified: Get mobile, send OTP (four digit number), verify it, and then show the account info: {account}.
    - IMPORTANT: You MUST get the user to confirm 'Yes, this is me' after showing account info before moving to loans.

    PHASE 2: LOANS
    - Only start this if 'Verified' is True.
    - User Account Data (Already Known): {known_info_str}
    - Ask for 'New' or 'Refinance' and call 'get_loan_requirements'.
    - Required info for this loan: {reqs}.
    
    STRATEGY FOR DATA COLLECTION:
    1. Look at the "User Account Data" above. 
    2. If a required field (like 'full_name') is already available in the account data (e.g., 'name'), DO NOT ask the user for it.
    3. Only ask the user for the fields that are in the "Required info" list but NOT present in the "User Account Data".
    4. You can suggest document upload to fill remaining fields.
    
    ELIGIBILITY:
    - Once you have all required fields (either from account data or user input), call 'check_loan_eligibility'.
    - If eligible, ask for permission to 'submit_loan_application'.
    """
    
    prompt = [SystemMessage(content=system_content)] + state["messages"]
    return {"messages": [llm.invoke(prompt)]}

def state_updater(state: AgentState):
    """Updates the 'is_verified' flag and account info based on tool results or user confirmation."""
    last_msg = state["messages"][-1]
    new_updates = {}

    # 1. Update account info from tool output
    if isinstance(last_msg, ToolMessage):
        try:
            content_data = ast.literal_eval(last_msg.content)
            if isinstance(content_data, dict) and "account_details" in content_data:
                new_updates["user_account"] = content_data["account_details"]
            if isinstance(content_data, list):
                new_updates["required_fields"] = content_data
        except:
            pass

    # 2. Check if user confirmed their identity to set 'is_verified'
    if not state.get("is_verified", False) and state.get("user_account"):
        # Check the most recent human message
        for m in reversed(state["messages"]):
            if isinstance(m, HumanMessage):
                text = m.content.lower()
                if any(word in text for word in ["yes", "correct", "it is me", "confirm", "that's me"]):
                    new_updates["is_verified"] = True
                break

    return new_updates

# --- Graph ---

builder = StateGraph(AgentState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(all_tools))
builder.add_node("updater", state_updater)

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "updater")
builder.add_edge("updater", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# --- FastAPI ---

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatInput(BaseModel):
    user_id: str
    text: str

@app.post("/chat")
async def chat_api(input_data: ChatInput):
    config = {"configurable": {"thread_id": input_data.user_id}}
    
    # Initialize keys if new session
    existing_state = await graph.aget_state(config)
    input_payload = {"messages": [HumanMessage(content=input_data.text)]}
    
    if not existing_state.values:
        input_payload.update({
            "is_verified": False,
            "user_account": {},
            "required_fields": []
        })

    output = await graph.ainvoke(input_payload, config)
    return {"response": output["messages"][-1].content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)