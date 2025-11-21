from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, random
from datetime import datetime
from asyncio import Queue

from  db.init_db import initDb
from managers.client_manager import ClientManager

app = FastAPI(lifespan=initDb)
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")

manager = ClientManager()

@app.get("/events")
async def events(req:Request):
    queue = Queue()
    client_id = int(req.cookies.get("client_id", -1))

    manager.add_client(client_id, queue)

    async def stream():
        try:
            while True:
                msg = await queue.get()
                yield msg
        finally:
            manager.remove_client(client_id)
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
    client_id = int(req.cookies.get("client_id", -1))

    await manager.selfClientMsg(client_id, f"event:clientConnected\ndata:{selfText}")

    await manager.excludeClientMsg(client_id, f"event:clientConnected\ndata:{newConnText}")

    return Response(status_code=204)

@app.post("/pushMessage")
async def message(req: Request, message: str=Form(...)):
    senderId = int( req.cookies['client_id'] )
    message = message.replace("\n", " ")
    time = datetime.now().strftime("%H:%M")

    await manager.writeMsgtoDb(senderId, message)

    def html(client_id) -> str:
        me = (senderId == client_id)
        if me:
            return f"event:messageDelivered\ndata:<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p></div>\n\n"
        else:
            return f"event:messageDelivered\ndata:<div class='leftMsg'><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>\n\n"

    for client_id, que in manager.clients.items():
        await que.put(html(client_id))

    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    client_id = req.cookies.get("client_id")
    if not client_id:
        client_id = str(random.randint(0,1000))

    respons = template.TemplateResponse(request=req, name="index.html")
    respons.set_cookie("client_id", client_id)

    return respons

@app.get("/test/{id}")
def test(id: int):
    print(id)
    return {"id_IS" : id}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
