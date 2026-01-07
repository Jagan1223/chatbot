from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.workflows.loan_graph import loan_graph

router = APIRouter()

class ChatInput(BaseModel):
    user_id: str
    text: str

@router.post("/chat")
async def chat(input: ChatInput):
    config = {"configurable": {"thread_id": input.user_id}}

    # 1️⃣ Fetch existing state
    existing_state = await loan_graph.aget_state(config)

    # 2️⃣ Always pass the new user message
    input_payload = {
        "messages": [HumanMessage(content=input.text)]
    }

    # 3️⃣ Initialize state ONLY for new sessions
    if not existing_state.values:
        input_payload.update({
            "is_verified": False,
            "account_exists": None,
            "user_account": {},
            "required_fields": [],
            "active_agent": "loan" 
        })

    # 4️⃣ Invoke graph
    result = await loan_graph.ainvoke(input_payload, config)

    return {
        "response": result["messages"][-1].content
    }
