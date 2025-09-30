from pydantic import BaseModel, Field
from typing import Literal
import uuid
from datetime import datetime

class Menu(BaseModel):
    name: str
    price: int
    coupon: int
    group_id: int
    soldout: bool

class Trsc(BaseModel):
    order_id: str
    group_id: int
    menu_name: str
    table_number: int
    payment_method: Literal['현금', '쿠폰']
    order_time: datetime = Field(default_factory=datetime.now)
    is_cooked: bool = False
    is_served: bool = False # 중앙 클라이언트에서 서빙 완료 여부를 관리하기 위해 추가

# 주문 클라이언트로부터 받을 데이터 모델
class TrscCreate(BaseModel):
    group_id: int
    menu_name: str
    table_number: int
    payment_method: Literal['현금', '쿠폰']


def read_menu():
    menu_list = []
    with open("../menu.txt", 'r') as menupage:
        for line in menupage:
            if line.strip().startswith('#') or not line.strip():
                continue
            tmp = line.split(',')
            each_menu = Menu(name=tmp[0], price=tmp[1], coupon=tmp[2], group_id=tmp[3], soldout=tmp[4])
            menu_list.append(each_menu)
    return menu_list