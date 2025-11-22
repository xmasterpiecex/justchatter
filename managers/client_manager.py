from asyncio import Queue

class ClientManager:
    def __init__(self) -> None:
        self.clients : dict[int, Queue] = {}

    def add_client(self, id: int, q: Queue):
        self.clients[id] = q

    def remove_client(self, id: int):
        self.clients.pop( id, None )

    async def broadcastMsg(self, sender_id:int, message: str, time):

        def html(client_id) -> str:
            me = (sender_id == client_id)
            if me:
                return f"event:messageDelivered\ndata:<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p></div>\n\n"
            else:
                return f"event:messageDelivered\ndata:<div class='leftMsg'><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>\n\n"

        for id, q in self.clients.items():
           await q.put(html(id))
