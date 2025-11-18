from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, random
from asyncio import Queue
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")


class ClientManager:
    def __init__(self) -> None:
        self.clients : dict[int, Queue] = {}

    def addClient(self, id: int, q: Queue):
        self.clients[id] = q

    def removeClient(self, id: int):
        self.clients.pop( id, None )

    async def selfClientMsg(self, clientId:int, data:str):
        if clientId in self.clients:
            await self.clients[clientId].put(data)

    async def excludeClientMsg(self, meId:int, data:str):
        for cid, q in self.clients.items():
            if meId != cid:
                await q.put(data)

    async def broadcastMsg(self, senderId:int, data: str):
        for id, q in self.clients.items():
           await q.put(data)

manager = ClientManager()

@app.get("/events")
async def events(req:Request):
    queue = Queue()
    clientId = int(req.cookies.get("clientId", -1))

    manager.addClient(clientId, queue)

    async def stream():
        try:
            while True:
                msg = await queue.get()
                yield msg
        finally:
            manager.removeClient(clientId)
            print(f"Client  disconnected")

    respons = StreamingResponse(stream(), media_type="text/event-stream", headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },)

    return respons

@app.get("/con", response_class=Response)
async def conn(req : Request):
    newConnText = "<div><----New client connected----></div>\n\n"
    selfText = "<div><----WELCOME TO CHAT BE NICE :)----></div>\n\n"
    clientId = int(req.cookies.get("clientId", -1))

    await manager.selfClientMsg(clientId, f"event:clientConnected\ndata:{selfText}")

    await manager.excludeClientMsg(clientId, f"event:clientConnected\ndata:{newConnText}")

    return Response(status_code=204)

@app.post("/pushMessage")
async def message(req: Request, message: str=Form(...)):
    senderId = int( req.cookies['clientId'] )
    message = message.replace("\n", " ")
    time = datetime.now().strftime("%H:%M")

    def html(clientId) -> str:
        me = (senderId == clientId)
        if me:
            return f"event:messageDelivered\ndata:<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p></div>\n\n"
        else:
            return f"event:messageDelivered\ndata:<div class='leftMsg'><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>\n\n"

    for clientId, que in manager.clients.items():
        await que.put(html(clientId))

    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    clientId = req.cookies.get("clientId")
    if not clientId:
        clientId = str(random.randint(0,1000))

    respons = template.TemplateResponse(request=req, name="index.html")
    respons.set_cookie("clientId", clientId)

    return respons


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
