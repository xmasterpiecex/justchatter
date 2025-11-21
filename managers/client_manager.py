from asyncio import Queue
from sqlalchemy import select
from db.base import AsyncSessionLocal
from db.models import Message, Client


class ClientManager:
    def __init__(self) -> None:
        self.clients : dict[int, Queue] = {}

    def add_client(self, id: int, q: Queue):
        self.clients[id] = q

    def remove_client(self, id: int):
        self.clients.pop( id, None )

    async def selfClientMsg(self, client_id:int, data:str):
        if client_id in self.clients:
            await self.clients[client_id].put(data)

    async def excludeClientMsg(self, me_id:int, data:str):
        for cid, q in self.clients.items():
            if me_id != cid:
                await q.put(data)

    async def broadcastMsg(self, sender_id:int, data: str):
        for id, q in self.clients.items():
           await q.put(data)

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
