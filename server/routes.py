from pathlib import Path
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
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


class VoiceSpeakRequest(BaseModel):
    text: str


class MemoryRequest(BaseModel):
    content: str


@router.get("/")
def home():
    return {"status": "online", "name": "Companion"}


@router.post("/chat")
def chat(request: ChatRequest):
    reply = agent.chat(request.message)
    return {"reply": reply}


@router.post("/voice")
def voice(request: VoiceRequest):
    result = voice_pipeline.run(duration=request.duration)
    return result


@router.post("/voice/upload")
async def voice_upload(audio: UploadFile = File(...)):
    upload_directory = Path("voice_uploads")
    upload_directory.mkdir(exist_ok=True)

    output_path = upload_directory / "latest.webm"

    content = await audio.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded voice audio is empty."
        )

    output_path.write_bytes(content)

    return {
        "status": "received",
        "filename": audio.filename,
        "content_type": audio.content_type,
        "size": len(content),
        "path": str(output_path)
    }


@router.post("/voice/transcribe")
def voice_transcribe():
    audio_path = Path("voice_uploads/latest.webm")

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No uploaded voice recording found."
        )

    try:
        result = voice_pipeline.input.stt.transcribe(
            audio_path
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    return result


@router.post("/voice/process")
def voice_process():
    audio_path = Path("voice_uploads/latest.webm")

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No uploaded voice recording found."
        )

    try:
        transcription = voice_pipeline.input.stt.transcribe(
            audio_path
        )

        text = transcription["text"].strip()

        if not text:
            return {
                "text": "",
                "reply": ""
            }

        reply = agent.chat(text)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:
        if audio_path.exists():
            audio_path.unlink()

    return {
        "text": text,
        "reply": reply
    }


@router.post("/voice/speak")
def voice_speak(request: VoiceSpeakRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Voice text cannot be empty."
        )

    temporary_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    output_path = Path(temporary_file.name)
    temporary_file.close()

    try:
        voice_pipeline.output.tts.synthesize(
            text,
            output_path
        )
    except Exception as error:
        if output_path.exists():
            output_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    cleanup_task = BackgroundTask(
        output_path.unlink,
        missing_ok=True
    )

    return FileResponse(
        path=output_path,
        media_type="audio/wav",
        filename="voice_output.wav",
        background=cleanup_task
    )


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

    return {"memory": memory}


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

