from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.config import OPENROUTER_API_KEY
from app.workflows.account_state import AccountState
from app.tools.account import submit_account_opening, transfer_back_to_loan_assistant

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
).bind_tools([submit_account_opening, transfer_back_to_loan_assistant])

def account_assistant(state: AccountState):
    system = SystemMessage(content="""
You are a Bank Account Opening Assistant.
Your goal is to collect details and open a bank account.

IMPORTANT:
1. If the user mentions they ALREADY have an account, use the `transfer_back_to_loan_assistant` tool immediately.
2. If the user wants to CANCEL or go back to the loan process, use the `transfer_back_to_loan_assistant` tool.
3. Once the account is successfully created using `submit_account_opening`, inform the user.
""")
    return {"messages": [llm.invoke([system] + state["messages"])]}