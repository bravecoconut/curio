# app/db.py

from pymongo import AsyncMongoClient
from beanie import init_beanie
from app.model.account import Account, User, Sessions, Post
from app.log.log import Logs


async def init_db():
    client = AsyncMongoClient("mongodb://localhost:27017")
    await init_beanie(
        database=client.rage,
        document_models=[Account, User, Sessions, Post, Logs],
    )