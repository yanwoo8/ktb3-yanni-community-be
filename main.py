# main.py
"""
FastAPI Application Entry Point

코드:
1. FastAPI의 기본 구조 작성 - app = FastAPI(), @app.get() 데코레이터
2. HTTP Response의 3요소 (Status Code, Headers, Body) 구현
3. JSON 직렬화 - Python dict → JSON string, JSONResponse
4. Cookie 세팅 - 세션ID를 식별자로 사용하는 쿠키 설정
"""

from typing import Dict
from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Community Backend",
    description="A simple Community backend project using FastAPI",
    version="0.1.0"
)



@app.get("/")
def root() -> Dict[str, str]:
    """
    루트 엔드포인트 (GET /)
    - 간단한 환영 메시지 반환하여 서비스 작동 확인 (Health Check)

    Returns:
    - Dict[str, str]: 환영 메시지 딕셔너리
    
    Note:
    - FastAPI는 Python dict를 자동으로 JSON으로 직렬화 (Content-Type: application/json)
    - 내부적으로 JSONResponse로 래핑됨
    """
    return {"message": "KTB AI 커뮤니티에 오신 것을 환영합니다!"}



@app.get("/custom")
def custom_response() -> JSONResponse:
    """
    HTTP Response의 3요소를 명시적으로 제어하는 엔드포인트 (GET /custom)
    - Status Code: 200 OK
    - Headers: 커스텀 헤더 포함
    - Body: JSON 데이터 포함
    
    HTTP Response 구조:
    1. Status Line: HTTP/1.1 200 OK
    2. Headers: 메타데이터 (Content-Type, Custom Headers 등)
    3. Body: 실제 전송 데이터 (JSON, HTML 등)
    
    Returns:
    - JSONResponse: 커스텀 헤더와 쿠키가 포함된 JSON 응답
    
    Note:
    - JSONResponse: FastAPI의 응답 클래스, Starlette의 Response를 상속
    - Cookie: HTTP의 Stateless 특성을 보완하는 클라이언트 측 저장소
    - session_id: 서버가 클라이언트를 식별하기 위한 고유 식별자
    """

    # Define Response Body (Content)
    content = {
        "status": "success",
        "data": "custom"
    }
    
    # Define Custom Headers (metadata)
    header = {
        "Kkotech-Custom-Header": "MyValue"
        #,"Access-Control-Expose-Headers": "Kkotech-Custom-Header"
        # 브라우저에서 JS가 이 헤더를 읽어야 하면 윗줄 주석 해제
        # CORS 정책으로 인해 브라우저가 커스텀 헤더에 접근할 수 있도록 허용
    }

    response = JSONResponse(status_code=200, # Status code := status_code
                            headers=header,  # Header := Headers
                            content=content) # Body := Content
    
    session_id: str = "abc123"
    response.set_cookie(key="session_id",
                        value=session_id,
                        samesite="lax") # CSRF 방어
    
    return response


"""
* uvicorn main:app --reload
* curl -v http://localhost:8000/custom

- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/
- 커스텀 응답: http://localhost:8000/custom
"""