from fastapi import FastAPI

from src.db.mongo import MongoEngine
from src.routes import machine_routes

db = MongoEngine().register_connection()
app = FastAPI()

app.include_router(machine_routes)
