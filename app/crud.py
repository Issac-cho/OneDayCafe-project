# app/crud.py

import sqlite3
from models import Trsc, Menu # Pydantic 모델 임포트

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
            order_id TEXT PRIMARY KEY,
            menu_name TEXT NOT NULL,
            table_number INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            order_time TEXT NOT NULL,
            is_cooked BOOLEAN NOT NULL,
            is_served BOOLEAN NOT NULL
        )
    ''')
    conn.execut('''
        CREATE TABLE IF NOT EXISTS order_counter (
            last_id INTEGER
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

    # 트랜잭션 시작: 다른 요청이 동시에 접근하지 못하도록 lock을 겁니다.
    cursor.execute("BEGIN IMMEDIATE")
    try:
        # 1. 현재 마지막 번호를 가져옵니다.
        cursor.execute("SELECT last_id FROM order_counter")
        last_id = cursor.fetchone()[0]

        # 2. 다음 번호를 계산합니다.
        next_id = last_id + 1

        # 3. DB에 다음 번호를 업데이트합니다.
        cursor.execute("UPDATE order_counter SET last_id = ?", (next_id,))

        # 4. 트랜잭션을 완료(commit)합니다.
        conn.commit()

        # 5. 네 자리 문자열 형식(예: 0001, 0332)으로 만들어 반환합니다.
        return f"{next_id:04d}"

    except Exception as e:
        conn.rollback() # 오류 발생 시 원상 복구
        raise e
    finally:
        conn.close()

# --- CRUD 함수들 ---

def create_trsc(trsc: Trsc):
    """새로운 주문(Trsc)을 DB에 추가 (Create)"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO trsc (order_id, group_id, menu_name, table_number, payment_method, order_time, is_cooked, is_served) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (trsc.order_id, trsc.group_id, trsc.menu_name, trsc.table_number, trsc.payment_method, trsc.order_time.isoformat(), trsc.is_cooked, trsc.is_served)
    )
    conn.commit()
    conn.close()

def get_all_trscs() -> list[Trsc]:
    """모든 주문 목록을 DB에서 조회 (Read)"""
    conn = get_db_connection()
    trsc_rows = conn.execute('SELECT * FROM trsc WHERE is_served = False').fetchall()
    conn.close()
    # DB에서 가져온 데이터를 Pydantic 모델 객체 리스트로 변환하여 반환
    return [Trsc(**row) for row in trsc_rows]

def get_group_trscs(group_id:int) -> list[Trsc]:
    conn = get_db_connection()
    sql = 'SELECT * FROM trsc WHERE group_id = ? AND is_served = False'
    trsc_rows = conn.execute(sql, (group_id,)).fetchall()
    conn.close()
    return [Trsc(**row) for row in trsc_rows]

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