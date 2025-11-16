from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, random
from asyncio import Queue
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")

clients = {}

@app.get("/events")
async def events(req:Request):
    queue = Queue()
    clients[queue] = int(req.cookies.get("clientId", -1))

    async def stream():
        try:
            while True:
                mess = await queue.get()
                yield mess
        finally:
            clients.pop(queue)
            print(f"Client  disconnected")

    respons = StreamingResponse(stream(), media_type="text/event-stream", headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },)
    return respons

@app.get("/con")
async def conn( req : Request):
    text = "<----New client has connected---->"

    for q in clients:
        await q.put(f"event:clientConnected\ndata:{text}\n\n")
    return {"status":200}

@app.post("/pushMessage")
async def message(req: Request, message: str=Form(...)):

    id = int( req.cookies['clientId'] )
    message = message.replace("\n", " ")
    time = datetime.now().strftime("%H:%M")

    for que, clientId in clients.items():
        me = (id == clientId)
        if me:
            htmlEl =f"<div class='rightMsg'><p class='rightTime'>{time}</p><p class='textMsg'>{message}</p></div>"
        else:
            htmlEl = f"<div class='leftMsg'><p class='textMsg'>{message}</p><p class='leftTime'>{time}</p></div>"

        response = f"event:messageDelivered\ndata: {htmlEl}\n\n"
        await que.put(response)

    return {"Status_Code": 200}

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
