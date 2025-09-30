from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from .models import *
from .crud import *

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)

manager = ConnectionManager()

#시작 페이지
@app.get("/", response_class=HTMLResponse)
def start_page_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# |GET|/order|주문 WebClient에게 order.html 페이지와 메뉴 목록을 렌더링하여 반환합니다.|
@app.get("/order", response_class=HTMLResponse)
def order_page_form(request: Request):
    menu_list = read_menu()
    return templates.TemplateResponse("order.html", {"request": request, "menulist": menu_list})

# |GET|/kitchen/{group_id}|요리 WebClient에게 kitchen.html 페이지를 렌더링하여 반환합니다.|
@app.get("/kitchen/{group_id}", response_class=HTMLResponse)
def kitchen_page_form(request: Request, group_id: str):
    trsc_list = get_group_trscs(group_id)
    return templates.TemplateResponse("kitchen.html", {"request": request, "trsclist": trsc_list})

# |GET|/central|중앙 WebClient에게 central.html 페이지를 렌더링하여 반환합니다.|
@app.get("/central", response_class=HTMLResponse)
def central_page_form(request: Request):
    trsc_list = get_all_trscs()
    return templates.TemplateResponse("kitchen.html", {"request": request, "trsclist": trsc_list})

# |POST|/api/order|주문 WebClient로부터 새 주문을 받아 DB에 추가하고, 웹소켓을 통해 연결된 클라이언트에게 모두 브로드캐스트합니다.|
@app.post("/api/order")
async def create_order(trsc_data: TrscCreate):
    next_order_id = get_next_order_id()
    new_trsc = Trsc(order_id=next_order_id, **trsc_data.model_dump())
    create_trsc(new_trsc)

    # 2. 생성 결과를 모든 웹소켓 클라이언트에게 방송
    all_trscs = get_all_trscs()
    await manager.broadcast({"type": "update", "data": [trsc.model_dump() for trsc in all_trscs]})
    
    # 3. 요청한 클라이언트에게는 HTTP로 직접 응답
    return {"message": "Order created successfully", "order_id": next_order_id}

# |PATCH|/api/trsc/{order_id}/cook|요리 WebClient로부터 요리 완료 요청을 받아 DB를 수정하고, 웹소켓을 통해 연결된 클라이언트에게 모두 브로드캐스트합니다.|
@app.patch("/api/trsc/{order_id}/cook")
async def cook_success(order_id:str):
    update_trsc_cooked_status(order_id)

    all_trscs = get_all_trscs()
    await manager.broadcast({"type": "update", "data": [trsc.model_dump() for trsc in all_trscs]})
    return {"message": "Cook successfully"}

# |PATCH|/api/trsc/{order_id}/serve|중앙 WebClient로부터 서빙 완료 요청을 받아 DB를 수정하고, 웹소켓을 통해 연결된 클라이언트에게 모두 브로드캐스트합니다.|
@app.patch("/api/trsc/{order_id}/serve")
async def serve_success(order_id:str):
    update_trsc_served_status(order_id)

    all_trscs = get_all_trscs()
    await manager.broadcast({"type": "update", "data": [trsc.model_dump() for trsc in all_trscs]})
    return {"message": "Serve successfully"}

# 웹소켓은 연결 및 방송 수신만 담당
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)