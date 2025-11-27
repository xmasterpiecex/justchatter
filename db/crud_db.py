from db.base import AsyncSessionLocal
from sqlalchemy import select
from db.models import Client, Message, Room

async def ensure_client_exists(client_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        if client is None:
            new_client = Client(id=client_id)
            session.add(new_client)
            await session.commit()

async def write_msg_to_db(room_id: int, sender_id: int, msg: str, time: str):
    await ensure_client_exists(sender_id)
    async with AsyncSessionLocal() as session:
        message = Message(room_id=room_id, client_id=sender_id, text=msg, timeStamp=time)
        session.add(message)
        await session.commit()

async def create_room(room_id:int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Room).where(Room.id == room_id))
        exist_room = result.scalar_one_or_none()
        if exist_room:
            print(f"[EXEPTION]'{exist_room}' room is already exist")
            return exist_room;

        room = Room(id=room_id)
        session.add(room)
        print(f"[CREATE]'{room}' room created")
        await session.commit()
