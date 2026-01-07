from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.config import OPENROUTER_API_KEY
from app.workflows.account_state import AccountState
from app.tools.account import submit_account_opening

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
).bind_tools([submit_account_opening])

def account_assistant(state: AccountState):
    system = SystemMessage(content="""
You are an Bank Account Opening Assistant.
Collect details and open a bank account.
""")
    print("Inside account_assistant....")

    return {"messages": [llm.invoke([system] + state["messages"])]}
