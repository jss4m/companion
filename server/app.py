from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .database import (
    initialize_database,
    cleanup_old_conversations,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()
cleanup_old_conversations()

app.include_router(router)