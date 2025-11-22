from asyncio import Queue

def conditional_html(sender_id: int, client_id: int, owner_data: str, foreign_data: str ) -> str:
    me = (sender_id == client_id)
    if me:
        return owner_data
    else:
        return foreign_data

class ClientManager:
    def __init__(self) -> None:
        self.clients : dict[int, Queue] = {}

    def add_client(self, id: int, q: Queue):
        self.clients[id] = q

    def remove_client(self, id: int):
        self.clients.pop( id, None )

    async def send_message(self, sender_id: int, sender_msg: str, reciver_msg: str):
        for id, q in self.clients.items():
           await q.put(conditional_html(sender_id, id, sender_msg, reciver_msg))
