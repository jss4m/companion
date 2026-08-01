from fastapi import FastAPI

from .routes import router
from .database import initialize_database


app = FastAPI()


initialize_database()


app.include_router(router)