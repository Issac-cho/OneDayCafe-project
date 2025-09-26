from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .models import *
from .crud import *

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class Board(BaseModel):
    title: str
    contents: str
    name: str



#시작 페이지
@app.get("/", response_class=HTMLResponse)
def start_page_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

GET	/order	주문 WebClient에게 order.html 페이지와 메뉴 목록을 렌더링하여 반환합니다.
@app.get("/order", response_class=HTMLResponse)
def order_page_form(request: Request):
    menu_list = []
    with open("../menu.txt", 'r') as menupage:
        for line in menupage:
            
    return templates.TemplateResponse("order.html", {"request": request})

# POST 처리: JSON으로 받을 때
@app.post("/boardapi")
def create_board(board: Board):
    return {"title": board.title, "contents": board.contents, "name": board.name}


# POST 처리: HTML 폼으로 받을 때
@app.post("/board", response_class=HTMLResponse)
def create_item_form(request: Request, title: str = Form(...), contents: str = Form(...), name: str = Form(...)):
    return templates.TemplateResponse("result.html", {"request": request, "title": title, "contents": contents, "name": name})
