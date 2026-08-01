from fastapi import FastAPI

from .routes import router
from .database import (
    initialize_database,
    cleanup_old_conversations,
)

app = FastAPI()


initialize_database()
cleanup_old_conversations()

app.include_router(router)