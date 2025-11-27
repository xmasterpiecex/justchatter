import asyncio
from asyncio import Queue

def conditional_html(sender_id: int, client_id: int, owner_data: str, foreign_data: str ) -> str:
    me = (sender_id == client_id)
    if me:
        return owner_data
    else:
        return foreign_data

class Room:
    def __init__(self):
        self.queue = asyncio.Queue();
        self.clients = {}

    async def broadcast(self, event, sender_id, sender_data, reciver_data):
        for id, q in self.clients.items():
            await q.put((event, conditional_html(sender_id, id, sender_data, reciver_data )))

    def add_client(self, client_id):
        self.clients[client_id] = asyncio.Queue()

    def remove_client(self, client_id):
        self.clients.pop(client_id)

class RoomsManager:
    def __init__(self) -> None:
        self.rooms = {}

    def get_room(self, room_name: str):
        if room_name not in self.rooms:
            self.rooms[room_name] = Room()
        return self.rooms[room_name]

    async def send_msg_to_room(self, room_name:str, msg: str):
        room = self.get_room(room_name)
        await room.send(msg)
