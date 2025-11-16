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

clients = set()

async def event_trigger(client_queue : Queue, req: Request):

    while True:
        client_message = await client_queue.get()
        client_id = int(req.cookies.get("clientId", -1))
        me = (client_id == client_message["id"])
        safe_msg = client_message['message'].replace("\n", " ")

        if me:
            htmlEl = (
                f"<div class='rightMsg'>"
                f"<p class='rightTime'>{client_message['time']}</p>"
                f"<p class='textMsg'>{safe_msg}</p></div>"
            )

        else:
            htmlEl = (
                f"<div class='leftMsg'>"
                f"<p class='textMsg'>{safe_msg}</p>"
                f"<p class='leftTime'>{client_message['time']}</p></div>"
            )
        response = (
            "event:messageDelivered\n"
            f"data: {htmlEl}\n\n"
        )

        yield response

@app.get("/events")
async def events(req:Request):
    queue = Queue()
    clients.add(queue)

    async def stream():
        try:
            async for msg_pkg in event_trigger(queue, req):
                yield msg_pkg
        finally:
            clients.remove(queue)
            print(f"Client  disconnected")

    respons = StreamingResponse(stream(), media_type="text/event-stream", headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },)
    return respons

@app.post("/pushMessage")
async def message(req: Request, message: str=Form(...)):

    dataPkg = {}
    dataPkg["message"] = message
    dataPkg[ "time" ] = datetime.now().strftime("%H:%M")
    dataPkg["id"] = int( req.cookies['clientId'] )

    for cl in clients:
        await cl.put(dataPkg)

    return {"Status_Code": 200}

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):

    if "clientId" not in req.cookies:
        clientId = random.randint(0,10000)
    else:
        clientId = int(req.cookies["clientId"])

    respons = template.TemplateResponse(request=req, name="index.html")

    if "clientId" not in req.cookies:
        respons.set_cookie("clientId", str( clientId ))

    return respons


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
