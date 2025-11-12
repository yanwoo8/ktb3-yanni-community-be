# main.py
"""
FastAPI Application Entry Point

Code 코드:
1. FastAPI의 기본 구조 작성 - app = FastAPI(), @app.get() 데코레이터
2. HTTP Response의 3요소 (Status Code, Headers, Body) 구현
3. JSON 직렬화 - Python dict → JSON string, JSONResponse
4. Cookie 세팅 - 세션ID를 식별자로 사용하는 쿠키 설정
5. REST API CRUD 구현 - POST(Create), GET(Read), PUT/PATCH(Update), DELETE(Delete) ⬅️ New✨

Endpoints 엔드포인트:
------- Basic Operations -------
- GET / : 루트 엔드포인트 (Health Check)
- GET /custom : 커스텀 응답 엔드포인트 (Status Code, Headers, Body 제어)
------- CRUD Operations -------
- POST /posts : 게시글 생성 엔드포인트
- GET /posts : 전체 게시글 조회 엔드포인트
- GET /posts/{post_id} : 특정 게시글 조회 엔드포인트
- PUT /posts/{post_id} : 게시글 전체 교체 엔드포인트
- PATCH /posts/{post_id} : 게시글 부분 수정 엔드포인트
- DELETE /posts/{post_id} : 게시글 삭제 엔드포인트



"""

from typing import Dict, Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(
    title="Community Backend",
    description="A simple Community backend project using FastAPI",
    version="0.1.0"
)



# ==================== Pydantic Models ====================

"""
Pydantic BaseModel의 역할:
1. 데이터 검증&변환 (Validation&Coercion): 타입 체크/변환, 필수 필드 검증
2. 직렬화/역직렬화 (Serialization): JSON ↔ Python Object
3. 자동 문서화: OpenAPI 스펙에 스키마 자동 등록
"""


class PostCreate(BaseModel):
    """
    [POST/PUT] 게시글 생성 요청 Request Body Schema (Pydantic Model)
    - title: 게시글 제목
    - content: 게시글 내용

    Note:
    - FastAPI는 Pydantic 모델을 보고 자동으로 request body를 파싱
    - 타입 힌트로 명시된 str은 런타임에 검증됨
    - 변환 가능한 경우 자동으로 변환 (예: int → str)
    """
    title: str
    content: str




class PostPartialUpdate(BaseModel):
    """
    [PATCH] 게시글 부분 수정을 위한 Request Body 스키마
    - title: 게시글 제목
    - content: 게시글 내용
    
    Note:
    - Optional[str]로 선언하여 클라이언트가 선택적으로 필드 전송 가능
    - None이 아닌 필드만 업데이트하는 방식으로 부분 수정 구현
    """
    title: Optional[str] = None
    content: Optional[str] = None




# ==================== In-Memory Storage ====================


posts = []  # global 임시 메모리 저장소 (서버 재시작 시 데이터 소실)


# ==================== Basic Endpoints ====================




@app.get("/") # 200: OK
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



@app.get("/custom") # 200: OK
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





# ==================== CRUD Endpoints =======================



# ======================= CREATE ===========================



@app.post("/posts", status_code=201) # 201: Created
def create_post(post: PostCreate) -> Dict:
    """
    게시글 생성 엔드포인트 (POST /posts)
    
    REST 원칙:
    - POST: 새로운 리소스 생성 (Non-idempotent)
    - Status Code 201: Created (리소스 생성 성공)
    - Location Header: 생성된 리소스의 URI 반환 (Best Practice)
    
    Args:
    - post (PostCreate): Request Body에서 파싱된 Pydantic 모델
    
    Returns:
    - Dict: 요청 처리 완료 메시지, 생성된 게시글 데이터
    
    Note:
    - Pydantic으로 모델을 dict로 변환하여 메모리 저장소에 추가
    - id는 서버에서 자동 생성 (Auto-increment 방식)
    """
    new_post = {
        "id": len(posts) + 1, # Auto-increment ID
        **post.model_dump()   # dict로 변환
    }

    posts.append(new_post)    # 메모리 저장소에 게시글 추가
    
    return {
        "message": "Created", 
        "data": new_post
    } # 반환값은 FastAPI가 자동으로 JSON으로 직렬화




# ======================= READ ===========================



# Read All

@app.get("/posts") # 200: OK
def get_all_posts() -> Dict:
    """
    전체 게시글 조회 엔드포인트 (GET /posts)
    
    REST 원칙:
    - GET: 리소스 조회 (Safe, Idempotent)
    - Collection Endpoint: 복수의 리소스 반환
    
    Returns:
    - Dict: 요청 처리 메시지, 전체 게시글 수, 전체 게시글 목록
    
    Note:
    - Pagination은 별도 구현 필요 (쿼리 파라미터: ?page=1&size=10)
    - 실제 서비스에서는 DB 쿼리 최적화 필요
    """

    return {
        "message": "Success",
        "count": len(posts),
        "data": posts
    }



# Read One

""" RESTful API에서의 매개변수 유형:
- Path Parameter: 리소스 식별자 (/posts/1) - 필수, URL 경로에 포함
- Query Parameter: 필터링/옵션 (?sort=desc) - 선택적, URL 쿼리 스트링
"""

@app.get("/posts/{post_id}") # 200: OK, 404: Not Found
def get_post(post_id: int) -> JSONResponse:
    """
    특정 게시글 조회 엔드포인트 (GET /posts/{post_id})
    
    Args:
    - post_id (int): URL 경로에서 추출된 게시글 ID (Path Parameter)
    
    Returns:
    - JSONResponse: 상태코드(200/404) + 내용 (게시글 데이터/에러 메시지)
    
    Note:
    - next(): 제너레이터에서 첫 번째 일치 항목 반환, 없으면 None
    - 404 Not Found: 요청한 리소스가 존재하지 않음
    """
    post = next((p for p in posts if p["id"] == post_id), None) # 검색: 게시글 ID 일치 여부
    
    # 404 Error: 찾는 게시글이 없으면
    if not post:
        return JSONResponse(
            status_code=404, 
            content={"error": "Not found",
                     "message": f"Post with id {post_id} does not exist"}
        )
    
    # 200 Success: 찾는 게시글이 있으면 출력
    return JSONResponse(
        status_code=200,
        content={"message": "Success", "data": post}
    )




# ======================= UPDATE ===========================



"""
PUT의 특징:
- Idempotent: 같은 요청을 여러 번 보내도 결과가 동일
- 전체 교체: 리소스의 모든 필드를 새 값으로 대체
- 클라이언트가 리소스의 전체 표현을 전송
- 서버는 누락된 필드를 기본값으로 설정하거나 오류 반환

PATCH의 특징:
- Non-idempotent: 같은 요청을 여러 번 보내면 결과가 달라질 수 있음 (구현에 따라 다를 수 있음)
- 부분 수정: 리소스의 일부 필드만 (전송된 필드만) 수정/업데이트
- 클라이언트가 수정할 필드만 선택적으로 전송

PATCH vs PUT:
- PUT: 리소스 전체 교체 (Idempotent) - 모든 필드 필수
- PATCH: 리소스 부분 수정 (Non-idempotent) - 일부 필드만 선택적으로 전송
"""


@app.put("/posts/{post_id}") # 200: OK, 404: Not Found
def update_post(post_id: int, post: PostCreate) -> JSONResponse:
    """
    게시글 전체 교체 엔드포인트 (PUT /posts/{post_id})
    
    Args:
    - post_id (int): 수정할 게시글 ID
    - post (PostCreate): 새로운 게시글 데이터 (전체 필드 필수)
    
    Returns:
    - JSONResponse: 상태코드(200/404) + 내용 (수정된 게시글 데이터/에러 메시지)
    
    Note:
    - 실제 DB에서는 UPDATE 쿼리 사용
    - 낙관적 잠금(Optimistic Locking)으로 동시성 제어 가능
    """

    # 대상 게시글 찾기
    for i, p in enumerate(posts):
        if p["id"] == post_id:

            # Full Change 전체 교체: ID는 유지, 나머지 필드는 새 값으로 대체
            updated_post = {
                "id": post_id,
                **post.model_dump()
            }
            posts[i] = updated_post
            
            # 200 Success: 수정 완료 응답
            return JSONResponse(
                status_code=200,
                content={"message": "Updated", "data": updated_post}
            )
    
    # 404 Error: 게시글이 없으면
    return JSONResponse(
        status_code=404,
        content={"error": "Not found",
                 "message": f"Post with id {post_id} does not exist"}
    )



@app.patch("/posts/{post_id}")
def partial_update(post_id: int, update_data: PostPartialUpdate) -> JSONResponse:
    """
    게시글 부분 수정 엔드포인트 (PATCH /posts/{post_id})
    
    Args:
    - post_id (int): 수정할 게시글 ID
    - update_data (PostPartialUpdate): 수정할 필드들 (Optional)
    
    Returns:
    - JSONResponse: 상태코드(200/404) + 내용 (수정된 게시글 데이터/에러 메시지)
    
    Note:
    - exclude_unset=True: 클라이언트가 보내지 않은 필드는 제외
    - 기존 값은 유지하고 전송된 필드만 업데이트
    """
    # 대상 게시글 찾기
    for i, p in enumerate(posts):
        if p["id"] == post_id:

            # Partial Update 부분 수정: None이 아닌 필드만 업데이트
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # 기존 게시글에 업데이트할 필드만 병합
            posts[i].update(update_dict)
            
            # 200 Success: 부분 수정 완료 응답
            return JSONResponse(
                status_code=200,
                content={"message": "Partially updated", "data": posts[i]}
            )
    
    # 404 Error: 게시글이 없으면
    return JSONResponse(
        status_code=404,
        content={"error": "Not found",
                 "message": f"Post with id {post_id} does not exist"}
    )




# ======================= DELETE ===========================



"""
DELETE의 특징:
- Idempotent: 같은 리소스를 여러 번 삭제해도 결과가 동일
- Status Code 204: No Content (삭제 성공, 응답 본문 없음)
- Status Code 404: Not Found (삭제할 리소스가 없음)
"""

@app.delete("/posts/{post_id}", status_code=204) # 204: No Content, 404: Not Found
def delete_post(post_id: int):
    """
    게시글 삭제 엔드포인트 (DELETE /posts/{post_id})
    
    Args:
    - post_id (int): 삭제할 게시글 ID
    
    Returns:
    - None (204 No Content) 또는 JSONResponse (404 Not Found)
    
    Note:
    - 204는 응답 본문이 없으므로 return 값이 무시됨
    - Soft Delete vs Hard Delete: DB에서 deleted_at 플래그 vs 실제 레코드 삭제
    """
    global posts  # 전역 변수 재할당을 위해 global 선언
    
    # 대상 게시글 찾기
    for i, p in enumerate(posts):
        if p["id"] == post_id:
            
            # 리스트에서 제거
            posts.pop(i)

            # 204 No Content: 본문 없이 상태 코드만 반환
            return None
    
    # 404 Error: 게시글이 없으면
    return JSONResponse(
        status_code=404,
        content={"error": "Not found",
                 "message": f"Post with id {post_id} does not exist"}
    )




# ==================== RUN ====================

"""
실행 방법:
* uvicorn main:app --reload

테스트 URL:
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/
- 커스텀 응답: http://localhost:8000/custom
- 게시글 목록: http://localhost:8000/posts

curl 테스트:
* GET: curl -X GET http://localhost:8000/posts
* POST: curl -X POST http://localhost:8000/posts -H "Content-Type: application/json" -d '{"title":"Test","content":"Hello"}'
* PUT: curl -X PUT http://localhost:8000/posts/1 -H "Content-Type: application/json" -d '{"title":"Updated","content":"World"}'
* PATCH: curl -X PATCH http://localhost:8000/posts/1 -H "Content-Type: application/json" -d '{"title":"Patched"}'
* DELETE: curl -X DELETE http://localhost:8000/posts/1
"""