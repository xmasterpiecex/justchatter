import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .base import engine, Base

@asynccontextmanager
async def initDb(app: FastAPI):
    retries = 3
    while retries:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception as err:
            print(f"[Connection] Data base not connected yet, =={retries}== tryies left")
            retries -= 1
            await asyncio.sleep(2)

    else:
        raise RuntimeError("Couldn't connect to Database")

    yield

    await engine.dispose()
