"""
FastAPI Application Entry Point (Refactored)

아키텍처:
Route → Controller → (향후: Model/Repository)
- Route: HTTP 계층 (요청/응답 처리)
- Controller: 비즈니스 로직 계층
- Schema: 데이터 검증 계층

변경사항:
- CRUD 로직을 post_routes.py로 이동
- 기본 엔드포인트(/, /custom)는 main.py에 유지
- include_router로 모듈화된 라우터 통합

Endpoints:
------- Basic Operations (main.py) -------
- GET /: Health Check
- GET /custom: 커스텀 응답 (Status Code, Headers, Cookie 제어)

------- CRUD Operations (post_routes.py) -------
- POST /posts: 게시글 생성
- GET /posts: 전체 게시글 조회
- GET /posts/{post_id}: 특정 게시글 조회
- PUT /posts/{post_id}: 게시글 전체 교체
- PATCH /posts/{post_id}: 게시글 부분 수정
- DELETE /posts/{post_id}: 게시글 삭제
"""

from typing import Dict
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routes import post_routes




# ==================== FastAPI App Setup ====================

app = FastAPI(
    title="Community Backend",
    description="A simple Community backend project using FastAPI with Router-Controller Architecture",
    version="0.2.0"  # version update after refactoring
)


# ==================== Router Registration ====================

"""
Router 등록:
- include_router: 모듈화된 라우터를 메인 앱에 통합
- prefix="/posts": 모든 엔드포인트에 /posts 접두사 추가
- tags=["posts"]: OpenAPI 문서에서 그룹화

장점:
1. 관심사의 분리: 게시글 관련 로직이 독립적인 모듈로 분리
2. 코드 재사용성: 다른 프로젝트에서 post_routes만 가져와 사용 가능
3. 유지보수성: 각 모듈의 책임이 명확하여 수정이 용이
"""
app.include_router(post_routes.router)


# In-Memory Storage 삭제 - 이제 Controller에서 관리
#posts = []


# ==================== Basic Endpoints ====================



@app.get("/")
def root() -> Dict[str, str]:
    """
    루트 엔드포인트 (GET /)
    - Health Check: 간단한 환영 메시지 반환하여 서비스 정상 작동 확인
    
    Returns:
    - Dict[str, str]: 환영 메시지
    """
    return {"message": "KTB AI 커뮤니티에 오신 것을 환영합니다!"}



@app.get("/custom") # 200: OK
def custom_response() -> JSONResponse:
    """
    커스텀 응답 엔드포인트 (GET /custom)
    - HTTP Response의 3요소 명시적 제어
    
    HTTP Response 구조:
    1. Status Line: HTTP/1.1 200 OK
    2. Headers: 메타데이터 (Content-Type, Custom Headers, etc.)
    3. Body: 실제 데이터 (JSON, HTML, etc.)
    
    Returns:
    - JSONResponse: 커스텀 헤더와 쿠키가 포함된 응답
    """

    # Response Body (Content)
    content = {
        "status": "success",
        "data": "custom"
    }
    
    # Custom Headers (metadata)
    header = {"Kkotech-Custom-Header": "MyValue"}

    response = JSONResponse(
        status_code=200, # Status code := status_code
        headers=header,  # Header := Headers
        content=content  # Body := Content
    )
    
    session_id: str = "abc123"
    response.set_cookie(
        key="session_id",
        value=session_id,
        samesite="lax"   # CSRF 방어
    )
    
    return response

# ==================== End of Code ====================




# ==================== RUN ====================

"""
실행 방법:
uvicorn app.main:app --reload

테스트 URL:
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/
- 커스텀 응답: http://localhost:8000/custom
- 게시글 목록: http://localhost:8000/posts

curl 테스트:
# CREATE
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Hello"}'


# READ ALL
curl -X GET http://localhost:8000/posts

# READ ONE
curl -X GET http://localhost:8000/posts/1

# UPDATE (PUT)
curl -X PUT http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated","content":"World"}'

# UPDATE (PATCH)
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Patched"}'

# DELETE
curl -X DELETE http://localhost:8000/posts/1
"""