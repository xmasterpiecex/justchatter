from fastapi import FastAPI
from contextlib import asynccontextmanager

from .base import engine, Base

@asynccontextmanager
async def initDb(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()
