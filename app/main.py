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
- GET /: Health Check or 메인 랜딩 페이지 리다이렉트
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
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from app.routes import post_routes, auth_routes, comment_routes, dev_routes




# ==================== FastAPI App Setup ====================

app = FastAPI(
    title="Community Backend",
    description="A simple Community backend project using FastAPI with Router-Controller Architecture",
    version="0.2.0"  # version update after refactoring
)

# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Exception Handlers ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic ValidationError를 한국어 경고 메시지로 변환하는 전역 예외 핸들러

    Args:
    - request (Request): FastAPI 요청 객체
    - exc (RequestValidationError): 요청 검증 오류

    Returns:
    - JSONResponse: 사용자 친화적인 한국어 오류 메시지
    """
    # 필드별 기본 오류 메시지 매핑
    field_messages = {
        'email': '*이메일을 입력해주세요.',
        'password': '*비밀번호를 입력해주세요',
        'password_confirm': '*비밀번호 확인을 입력해주세요',
        'nickname': '*닉네임을 입력해주세요',
        'profile_image': '*프로필 이미지를 입력해주세요'
    }

    errors = exc.errors()

    if not errors:
        return JSONResponse(
            status_code=400,
            content={"detail": "입력값을 확인해주세요."}
        )

    # 첫 번째 에러만 처리 (보통 하나씩 처리하는 것이 UX에 좋음)
    first_error = errors[0]
    field = first_error['loc'][-1] if first_error['loc'] else 'unknown'
    error_type = first_error['type']

    # ValueError가 있으면 커스텀 메시지 우선 사용
    if error_type == 'value_error':
        msg = first_error.get('msg', '')
        # 이메일 형식 오류 체크
        if 'email' in msg.lower():
            message = "*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)"
        else:
            ctx = first_error.get('ctx', {})
            if 'error' in ctx:
                message = str(ctx['error'])
            else:
                # msg에서 ValueError 메시지 추출
                if 'Value error,' in msg:
                    message = msg.split('Value error,')[-1].strip()
                else:
                    message = msg
    # missing 필드인 경우
    elif error_type == 'missing':
        message = field_messages.get(field, f'*{field}을(를) 입력해주세요.')
    # 이메일 형식 오류
    elif error_type in ['value_error.email', 'email']:
        message = "*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)"
    # 문자열 길이 제약 위반
    elif error_type in ['string_too_short', 'string_too_long']:
        if field == 'email':
            message = "*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)"
        elif field == 'password':
            message = "*비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."
        elif field == 'nickname':
            message = "*닉네임은 최대 10자 까지 작성 가능합니다."
        else:
            message = field_messages.get(field, "입력값을 확인해주세요.")
    # JSON 파싱 에러
    elif error_type == 'json_invalid':
        message = "입력값을 확인해주세요."
    # 기타 에러
    else:
        message = field_messages.get(field, "입력값을 확인해주세요.")

    return JSONResponse(
        status_code=400,
        content={"detail": message}
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
app.include_router(auth_routes.router)
app.include_router(comment_routes.router)
app.include_router(dev_routes.router)  # 개발/테스트용 라우터

# Static Files (정적 파일 서빙)
app.mount("/static", StaticFiles(directory="static"), name="static")


# In-Memory Storage 삭제 - 이제 Controller에서 관리
#posts = []


# ==================== Basic Endpoints ====================



@app.get("/")
def root():
    """
    루트 엔드포인트 (GET /)
    - 헬스 체크
    - 메인 랜딩 페이지로 리다이렉트

    Returns:
    - RedirectResponse: /static/index.html로 리다이렉트
    """
    return {"message": "Community Backend is running."}
    #return RedirectResponse(url="/static/index.html")



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