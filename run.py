# run.py

import uvicorn
from app.main import app  # app/main.py에서 app 객체를 가져옵니다.

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # FastAPI 앱의 위치 (모듈:객체)
        host="127.0.0.1",  # 접속할 호스트 주소
        port=8000,         # 접속할 포트 번호
        reload=False        # 코드 변경 시 서버 자동 재시작
    )