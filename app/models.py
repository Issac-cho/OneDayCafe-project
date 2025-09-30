from pydantic import BaseModel, Field
from typing import Literal
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