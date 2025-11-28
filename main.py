from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn, random
from datetime import datetime
from dotenv import load_dotenv
import os

from db.init_db import initDb
from db.crud_db import create_client, write_msg_to_db, create_room
from managers.rooms_manager import RoomsManager

load_dotenv()

SECRET_KEY = os.getenv("Session_Middleware_SECRET_KEY")

app = FastAPI(lifespan=initDb)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=f"{SECRET_KEY}")
template = Jinja2Templates(directory="templates")

room_manager = RoomsManager()

@app.get("/events/{room_name}")
async def events(room_name:str, req:Request):
    room = room_manager.get_room(room_name)
    client_id = req.cookies.get("client_id") or str(id(req))

    room.add_client(client_id)
    q = room.clients[client_id]

    async def stream():
        try:
            while True:
                if await req.is_disconnected():
                    print(f"Client  disconnected")
                    req.cookies.clear()
                    break

                ev, html = await q.get()
                msg = f"event:{ev}\ndata:{html}\n\n"

                yield msg
        finally:
            print("Client disconnected")
            room.remove_client(client_id)

    respons = StreamingResponse(stream(), media_type="text/event-stream", headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },)

    return respons

@app.post("/pushMessage/{room_name}")
async def message(room_name:str, req: Request, message: str=Form(...)):
    sender_id = req.cookies['client_id']
    message = message.replace("\n", " ")
    time = datetime.now().strftime("%H:%M")
    name = req.session.get("name", "Uknown")

    sender_data = f"<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p><p class='rightName'>{name}</p></div>"
    reciver_data = f"<div class='leftMsg'><p class='leftName'>{name}</p><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>"

    room = room_manager.get_room(room_name)
    await write_msg_to_db(room_name, sender_id, message, time)

    await room.broadcast("message_delivered", sender_id, sender_data, reciver_data)

    return Response(status_code=204)

@app.get("/conn/{room_name}")
async def welcome_msg(room_name:str, req: Request):
    sender_id = req.cookies['client_id']
    sender_data = f"<div class='hiMessage'>Welome to chat</div>\n\n"
    reciver_data = f"<div class='hiMessage'>New client joined to chat</div>\n\n"

    room = room_manager.get_room(room_name)
    client_name = req.session.get("name", "Uknown")
    await room.broadcast("client_connected", sender_id, sender_data, reciver_data)
    await create_client(client_name, sender_id, room_name)

    return Response(status_code=204)

@app.get("/chat/{room_name}", response_class=HTMLResponse)
async def index(room_name: str, req: Request):
    client_id = req.cookies.get("client_id")

    if not client_id:
        client_id = str(random.randint(0,1000))

    name = req.session.get("name", "Uknown")
    data = {
        "room_name" : room_name,
        "client_name": name
    }

    respons = template.TemplateResponse(request=req, name="index.html", context={"data": data})
    respons.set_cookie("client_id", client_id)

    return respons

@app.get("/log", response_class=HTMLResponse)
async def loginin_page(req: Request):

    req.cookies.clear()

    respons = template.TemplateResponse(request=req, name="login_page.html")

    return respons

@app.post("/enter", response_class=Response)
async def enter_to_chat(req:Request, room: str=Form(...), name: str=Form(...)):
    room = room.replace("\n", " ")
    name = name.replace("\n", " ")
    req.session["name"]= name
    await create_room(room)

    return Response(status_code=200, headers={"HX-Redirect": f"/chat/{room}"})


@app.get("/", response_class=RedirectResponse)
async def redirection():
    return RedirectResponse("/log")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
