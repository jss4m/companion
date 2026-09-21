from fastapi import APIRouter, HTTPException
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


class MemoryRequest(BaseModel):
    content: str


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
def pin_memory(request: MemoryRequest):
    saved = agent.memory.add_pinned_memory(
        request.content
    )

    return {
        "status": "saved" if saved else "already_exists",
        "memory": request.content
    }


@router.get("/memory")
def get_memories():
    return {
        "memories": agent.memory.get_pinned_memories_with_ids()
    }


@router.put("/memory/{memory_id}")
def update_memory(
    memory_id: int,
    request: MemoryRequest
):
    updated = agent.memory.update_pinned_memory(
        memory_id,
        request.content
    )

    if updated == -1:
        raise HTTPException(
            status_code=409,
            detail="Another memory already contains that information."
        )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Memory not found."
        )

    memories = agent.memory.get_pinned_memories_with_ids()

    memory = next(
        (
            memory
            for memory in memories
            if memory["id"] == memory_id
        ),
        None
    )

    return {
        "memory": memory
    }


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: int):
    deleted = agent.memory.delete_pinned_memory_by_id(
        memory_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found."
        )

    return {
        "status": "deleted",
        "id": memory_id
    }