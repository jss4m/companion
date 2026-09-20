from fastapi import APIRouter
from pydantic import BaseModel

from .agent import Agent
from .voice.pipeline import VoicePipeline


router = APIRouter()

agent = Agent()

voice_pipeline = VoicePipeline(
    agent=agent,
    model_path="models/voices/en_US-lessac-medium.onnx"
)


class ChatRequest(BaseModel):
    message: str


class VoiceRequest(BaseModel):
    duration: int = 5


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


@router.post("/voice")
def voice(request: VoiceRequest):
    result = voice_pipeline.run(
        duration=request.duration
    )

    return result


@router.post("/memory/pin")
def pin_memory(content: str):
    agent.memory.add_pinned_memory(content)

    return {
        "status": "saved",
        "memory": content
    }
