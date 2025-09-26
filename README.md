# OneDayCafe-project
일일카페 주문/확인 시스템

## <용어 정의>
# 메뉴
- 이름, 가격, 그룹(1 이상의 정수)에 대한 정보를 담고 있는 객체
# 그룹
- 메뉴를 담당하는 요리 client 의 종류
- 한 그룹이 모든 메뉴를 담당할 수도 있고, 한 메뉴를 여러 그룹이 담당할 수도 있다.
# trsc
- 주문 번호, 메뉴, 테이블 번호, 지불방식(현금 / 쿠폰 택 1), 주문시각, 요리 완성 여부, 서빙 완료 여부 에 대한 정보를 담고 있다.
- 메뉴는 menu.txt 를 읽어옴
# trsc list
- 생성된 trsc 들 중 삭제되지 않은 trsc 들의 모임

## <시스템 아키텍처>
# WAS
- 주문 webClient 로부터 주문을 입력 받으면 trsc list 에 해당 주문을 추가한 후 요리 webClient와 중앙 webClient에게 trsc list를 전송
- 주문 입력 받을 시 그 trsc 데이터 저장 (txt 파일 등을 열어서 작성해도 괜찮음)
- 요리 webClient 로부터 요리 완성 메시지를 받으면 trsc list 안의 해당 주문이 완성되었음으로 수정 후 요리 webClient와 중앙 webClient에게 trsc list 전송
- 중앙 webClient 로부터 trsc 삭제 요청을 받으면 trsc list 안의 해당 주문을 삭제 후 요리 webClient와 중앙 webClient에게 trsc list 전송

# 주문 webClient
- 5-6개 정도 WAS에 동시 접속
- WAS에게 주문 페이지 html을 요청한 뒤, trsc을 작성하여 전송

# 요리 webClient
- 6개 정도 WAS에 동시 접속
- 그룹 1-6 중 하나 선택
- WAS에게 trsc list를 받으면, trsc list를 보여주되, 자신의 그룹에 속한 메뉴만 더 강조하여 보여준 뒤 완성 여부 버튼 활성화
- 요리가 완성되어 완성 여부 버튼을 클릭하면, WAS에게 해당 trsc이 완성되었음을 전송

# 중앙 webClient
- 1개 WAS에 접속
- WAS에게 trsc list 를 받으면, 모든 trsc list를 보여주되, 완성된 trsc 을 구분할 수 있도록 한다.
- 완성된 trsc 의 서빙이 완료되면 WAS에게 trsc 삭제 요청을 전송

## <활용 기술스택>
Backend: FastAPI
Frontend: HTML, CSS, JavaScript (Jinja2 템플릿)
Others: Python requests, openai, uvicorn