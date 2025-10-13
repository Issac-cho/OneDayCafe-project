# app/crud.py

import sqlite3
from .models import Order, Trsc, Menu # Pydantic 모델 임포트

DATABASE_FILE = "cafe.db"

def get_db_connection():
    """데이터베이스 연결 객체를 반환하는 함수"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # 결과를 딕셔너리처럼 접근 가능하게 함
    return conn

def init_db():
    """애플리케이션 시작 시 호출되어 테이블을 생성하는 함수"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS trsc (
            trsc_id TEXT PRIMARY KEY,
            menu_num INTEGER NOT NULL,
            table_num INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            order_time TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS order (
            trsc_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            menu_name TEXT NOT NULL,
            group_id INTEGER NOT NULL,
            count INTEGER NOT NULL,     
            is_cooked BOOL FALSE,
            is_served BOOL FALSE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS order_counter (
            last_trsc_id INTEGER
            last_order_id INTEGER
        )
    ''')
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM order_counter")
    if cursor.fetchone()[0] == 0:
        conn.execute("INSERT INTO order_counter (last_id) VALUES (0)")

    conn.commit()
    conn.close()
    # menu 테이블 생성 로직도 추가할 수 있습니다.

def get_next_order_id() -> str:
    """다음 주문 번호를 생성하고 DB에 업데이트한 뒤 반환"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("BEGIN IMMEDIATE")
    try:
        cursor.execute("SELECT last_order_id FROM order_counter")
        last_order_id = cursor.fetchone()[0]
        next_order_id = last_order_id + 1
        cursor.execute("UPDATE order_counter SET last_order_id = ?", (next_order_id,))
        conn.commit()
        return f"{next_order_id:02d}"

    except Exception as e:
        conn.rollback() # 오류 발생 시 원상 복구
        raise e
    finally:
        conn.close()

def get_next_trsc_id() -> str:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("BEGIN IMMEDIATE")
    try:
        cursor.execute("SELECT last_trsc_id FROM order_counter")
        last_trsc_id = cursor.fetchone()[0]
        next_trsc_id = last_trsc_id + 1
        cursor.execute("UPDATE order_counter SET last_trsc_id = ?, last_order_id = 0", (next_trsc_id,))
        conn.commit()
        return f"{next_trsc_id:05d}"

    except Exception as e:
        conn.rollback() # 오류 발생 시 원상 복구
        raise e
    finally:
        conn.close()

# --- CRUD 함수들 ---

def create_trsc(trsc: Trsc):
    """새로운 주문(Trsc)을 DB에 추가 (Create)"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO trsc (trsc_id, menu_num, table_num, payment_method, order_time)
        VALUES (?,?,?,?,?)
        ''', (trsc.trsc_id, len(trsc.orders), trsc.table_num, trsc.payment_method, trsc.order_time)
    )
    for od in trsc.orders:
        conn.execute('''
            INSERT INTO order (trsc_id, order_id, menu_name, group_id, count, is_cooked, is_served)
            VALUES (?,?,?,?,?,?,?)
        ''', (trsc.trsc_id, od.order_id, od.menu_name, od.group_id, od.count, od.is_cooked, od.is_served)
        )
    conn.commit()
    conn.close()

def get_all_orders() -> list[Order]:
    """모든 주문 목록을 DB에서 조회 (Read)"""
    conn = get_db_connection()
    trsc_rows = conn.execute('SELECT * FROM trsc WHERE is_served = False').fetchall()
    conn.close()
    # DB에서 가져온 데이터를 Pydantic 모델 객체 리스트로 변환하여 반환
    return [Order(**row) for row in trsc_rows]

def get_group_orders(group_id:int) -> list[Order]:
    conn = get_db_connection()
    sql = 'SELECT * FROM trsc WHERE group_id = ? AND is_served = False'
    trsc_rows = conn.execute(sql, (group_id,)).fetchall()
    conn.close()
    return [Order(**row) for row in trsc_rows]

def update_trsc_cooked_status(order_id: str):
    """특정 주문의 요리 완료 상태를 True로 변경 (Update)"""
    conn = get_db_connection()
    conn.execute('UPDATE trsc SET is_cooked = ? WHERE order_id = ?', (True, order_id))
    conn.commit()
    conn.close()

def update_trsc_served_status(order_id: str):
    conn = get_db_connection()
    conn.execute('UPDATE trsc SET is_served = ? WHERE order_id = ?', (True, order_id))
    conn.commit()
    conn.close()

def delete_trsc(order_id: str):
    """특정 주문을 DB에서 삭제 (Delete)"""
    conn = get_db_connection()
    conn.execute('DELETE FROM trsc WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()

def read_menu() -> list[Menu]:
    menu_list = []
    with open("menu.txt", 'r', encoding='utf-8') as menupage:
        for line in menupage:
            if line.strip().startswith('#') or not line.strip():
                continue
            tmp = [item.strip() for item in line.split(',')]
            each_menu = Menu(
                name=tmp[0],
                price=int(tmp[1]),
                coupon=int(tmp[2]),
                group_id=int(tmp[3]),
                soldout=(tmp[4].lower() == 'true')
            )
            menu_list.append(each_menu)
    return menu_list

if __name__ == "__main__":
    init_db()
    new_order = Trsc(
        menu_name="아이스 아메리카노",
        table_number=5,
        payment_method="현금"
    )
    create_trsc(new_order)
    list = get_all_trscs()
    print(list)