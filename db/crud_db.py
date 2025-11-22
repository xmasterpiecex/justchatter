from db.base import AsyncSessionLocal
from sqlalchemy import  select
from db.models import Client, Message

async def ensure_client_exists(self, client_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        if client is None:
            new_client = Client(id=client_id)
            session.add(new_client)
            await session.commit()

async def writeMsgtoDb(self, id: int, msg: str):
    await self.ensure_client_exists(id)
    async with AsyncSessionLocal() as session:
        message = Message(client_id=id, text=msg)
        session.add(message)
        await session.commit()
