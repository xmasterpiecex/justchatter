from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, random
from datetime import datetime
from asyncio import Queue

from db.init_db import initDb
from db.crud_db import write_msg_to_db, create_room
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

@app.post("/pushMessage/{room_id}")
async def message(room_id:int, req: Request, message: str=Form(...)):
    sender_id = int( req.cookies['client_id'] )
    message = message.replace("\n", " ")
    time = datetime.now().strftime("%H:%M")

    clients_pkg = f"event:message_delivered\ndata:<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p></div>\n\n"
    foreign_pkg = f"event:message_delivered\ndata:<div class='leftMsg'><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>\n\n"

    await manager.send_message(sender_id, clients_pkg, foreign_pkg)
    await write_msg_to_db(room_id, sender_id, message, time)

    return Response(status_code=204)

@app.get("/conn/{room_id}")
async def conn(room_id: int,req: Request):
    sender_id = int(req.cookies['client_id'])
    clients_pkg = f"event:client_connected\ndata:<div class='hiMessage'>Welome to chat</div>\n\n"
    foreign_pkg = f"event:client_connected\ndata:<div class='hiMessage'>New client joined to chat</div>\n\n"

    await manager.send_message(sender_id, clients_pkg, foreign_pkg)
    await create_room(room_id)

    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    client_id = req.cookies.get("client_id")
    if not client_id:
        client_id = str(random.randint(0,1000))

    respons = template.TemplateResponse(request=req, name="index.html")
    respons.set_cookie("client_id", client_id)

    return respons


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
