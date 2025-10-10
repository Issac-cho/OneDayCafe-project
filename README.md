# OneDayCafe-project
일일카페 주문/확인 시스템

## <용어 정의>
### 메뉴
- 이름, 가격, 그룹(1 이상의 정수)에 대한 정보를 담고 있는 객체
### 그룹
- 메뉴를 담당하는 요리 client 의 종류
- 한 그룹이 모든 메뉴를 담당할 수도 있고, 한 메뉴를 여러 그룹이 담당할 수도 있다.
### order
- Order 번호, 메뉴 이름, 개수, 요리 완성 여부, 서빙 완료 여부
### trsc
- Trsc 번호, order, 테이블 번호, 지불방식(현금 / 쿠폰 택 1), 주문시각 에 대한 정보를 담고 있다.
- 메뉴는 menu.txt 를 읽어옴
### 완료
- trsc의 요리 완성 여부와 서빙 완료 여부가 모두 True 인 상태
### trsc list
- 생성된 trsc 들 중 완료되지 않은 trsc 들의 모임

## <시스템 아키텍처>
### WAS (app/main.py)
- 주문 webClient 로부터 주문을 입력 받으면 trsc list 에 해당 주문을 추가한 후 요리 webClient와 중앙 webClient에게 trsc list를 전송
- 주문 입력 받을 시 그 trsc 데이터 저장
- 요리 webClient 로부터 요리 완성 메시지를 받으면 trsc list 안의 해당 주문이 완성되었음으로 수정 후 요리 webClient와 중앙 webClient에게 trsc list 전송
- 중앙 webClient 로부터 trsc 삭제 요청을 받으면 trsc list 안의 해당 주문을 삭제 후 요리 webClient와 중앙 webClient에게 trsc list 전송

|Method|Path|설명|
|------|---|---|
|GET|/order|주문 WebClient에게 order.html 페이지와 메뉴 목록을 렌더링하여 반환합니다.|
|GET|/kitchen/{group_id}|요리 WebClient에게 kitchen.html 페이지를 렌더링하여 반환합니다.|
|GET|/central|중앙 WebClient에게 central.html 페이지를 렌더링하여 반환합니다.|
|POST|/api/order|주문 WebClient로부터 새 주문을 받아 DB에 추가하고, 웹소켓을 통해 연결된 클라이언트에게 모두 브로드캐스트합니다.|
|PATCH|/api/trsc/{order_id}/cook|요리 WebClient로부터 요리 완료 요청을 받아 DB를 수정하고, 웹소켓을 통해 연결된 클라이언트에게 모두 브로드캐스트합니다.|
|PATCH|/api/trsc/{order_id}/serve|중앙 WebClient로부터 서빙 완료 요청을 받아 DB를 수정하고, 웹소켓을 통해 연결된 클라이언트에게 모두 브로드캐스트합니다.|

### Database (app/cafe.db)
- Sqlite
- trsc이 생성될 때마다 데이터 생성 후 저장(주문번호, 메뉴, 테이블번호, 지불방식, 주문시각, 요리완성여부, 서빙완료여부)
- WAS 가 요청하면 완료되지 않은 trsc들의 list를 반환

### 주문 webClient
- 5-6개 정도 WAS에 동시 접속
- WAS에게 주문 페이지 html(app/templates/order.html)을 요청
- User가 trsc을 작성하여 전송

### 요리 webClient
- N개 WAS에 동시 접속
- 그룹 1-N 중 하나 선택
- WAS에게 요리 페이지 html(app/templates/kitchen.html/?group_id=={그룹번호})을 요청
- WAS에게 trsc list를 받으면, trsc list를 보여주되, 자신의 그룹에 속한 메뉴만 더 강조하여 보여준 뒤 완성 여부 버튼 활성화
- 요리가 완성되어 완성 여부 버튼을 클릭하면, WAS에게 해당 요리 완료 요청을 전송

### 중앙 webClient
- 1개 WAS에 접속
- WAS에게 중앙 페이지 html(app/templates/central.html)을 요청
- WAS에게 trsc list 를 받으면, 모든 trsc list를 보여주되, 완성된 trsc 을 구분할 수 있도록 한다.
- 완성된 trsc 의 서빙 여부 버튼을 클릭하면 WAS에게 trsc 서빙 완료 요청을 전송

## <활용 기술스택>
- Backend: FastAPI
- Frontend: HTML, CSS, JavaScript (Jinja2 템플릿)
- Database: SQLite
- Others: Python requests, uvicorn