from db.base import AsyncSessionLocal
from sqlalchemy import select, desc
from db.models import Client, Message, Room

async def ensure_client_exists(client_name: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).where(Client.client_name == client_name))
        client = result.scalar_one_or_none()
        if client is None:
            raise ValueError(f"[DB ERR] Client '{client}' does not exist")
        return client

async def ensure_room(room_name: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Room).where(Room.room_name == room_name))
        room = result.scalar_one_or_none()
        if room is None:
            raise ValueError(f"[DB ERR] Room '{room_name}' does not exist")
        return room

async def write_msg_to_db(room_name: str, sender_id: str, msg: str, time: str):
    client = await ensure_client_exists(sender_id)
    room = await ensure_room(room_name)
    async with AsyncSessionLocal() as session:
        message = Message(room_id=room.id, client_id=client.id, text=msg, client_name=client.client_name, timeStamp=time)
        session.add(message)
        await session.commit()

async def create_client(client_name: str, room_name:str):
    room = await ensure_room(room_name)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).where(Client.client_name == client_name))
        client = result.scalar_one_or_none()

        if client is None:
            client = Client(client_name=client_name, room_id=room.id)
            session.add(client)
            await session.commit()
            await session.refresh(client)
        return client

async def create_room(room_name:str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Room).where(Room.room_name == room_name))
        exist_room = result.scalar_one_or_none()
        if exist_room:
            print(f"[EXEPTION]'{exist_room}' room is already exist")
            return exist_room;

        room = Room(room_name=room_name)
        session.add(room)
        await session.commit()
        await session.refresh(room)
        return room

async def get_messages_from_room(room_name: str):
    room = await ensure_room(room_name)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Message).where(Message.room_id == room.id).order_by(desc( Message.id)))
        messages = result.scalars().all()
        return messages
