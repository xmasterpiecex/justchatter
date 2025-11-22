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

    async def send_hi_message(self, sender_id: int):
        clients_pkg = f"event:client_connected\ndata:<div class='hiMessage'>Welome to chat</div>\n\n"
        foreign_pkg = f"event:client_connected\ndata:<div class='hiMessage'>New client joined to chat</div>\n\n"

        for id, q in self.clients.items():
           await q.put(conditional_html(sender_id, id, clients_pkg, foreign_pkg))

    async def send_message(self, sender_id:int, message: str, time):
        clients_pkg = f"event:message_delivered\ndata:<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p></div>\n\n"
        foreign_pkg = f"event:message_delivered\ndata:<div class='leftMsg'><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>\n\n"

        for id, q in self.clients.items():
           await q.put(conditional_html(sender_id, id, clients_pkg, foreign_pkg))
