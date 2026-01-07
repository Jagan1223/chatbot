from fastapi import FastAPI
from app.api.chat import router
from app.db.models import init_db
from fastapi.middleware.cors import CORSMiddleware

init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
