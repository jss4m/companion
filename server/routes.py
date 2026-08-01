from fastapi import APIRouter
from pydantic import BaseModel

from .agent import Agent

router = APIRouter()

agent = Agent()


class ChatRequest(BaseModel):
    message: str


@router.get("/")
def home():
    return {
        "status": "online",
        "name": "Companion",
    }


@router.post("/chat")
def chat(request: ChatRequest):
    reply = agent.chat(request.message)

    return {
        "reply": reply
    }