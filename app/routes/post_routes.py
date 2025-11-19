"""
Post Routes

역할:
1. HTTP 요청/응답 처리: Request → Controller → Response
2. 상태 코드 매핑: Controller 예외 → HTTP Status Code
3. 경로 라우팅: URL 패턴 정의

설계 원칙:
- 얇은 계층(Thin Layer): 비즈니스 로직은 Controller에 위임
- 단일 책임 원칙(SRP): HTTP 계층만 담당
- 의존성 주입: Controller 인스턴스를 주입받아 사용

Note:
- APIRouter: FastAPI의 모듈화된 라우팅 시스템
- HTTPException: FastAPI의 HTTP 예외 클래스

Endpoints:
- POST /posts: 게시글 생성
- GET /posts: 전체 게시글 조회
- GET /posts/{post_id}: 특정 게시글 조회

- PUT /posts/{post_id}: 게시글 전체 수정
- PATCH /posts/{post_id}: 게시글 부분 수정
- DELETE /posts/{post_id}: 게시글 삭제

- POST /posts/{post_id}/like: 게시글 좋아요 토글
- GET /posts/{post_id}/is-liked: 게시글 좋아요 상태 확인
- DELETE /posts/{post_id}/like: 게시글 좋아요 취소
"""


from typing import Dict
from fastapi import APIRouter, HTTPException
from app.schemas.post_schema import PostCreate, PostPartialUpdate
from app.controllers.controller_instances import post_controller
import logging



# ==================== Router Setup ====================


# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/posts",    # URL prefix: /posts
    tags=["posts"]      # OpenAPI 문서화 그룹
)


# Controller 인스턴스 (공유 Singleton)
controller = post_controller


# Logger 인스턴스 생성
logger = logging.getLogger(__name__)



# ==================== CREATE ====================


"""REST - POST
- POST: 새로운 리소스 생성 (Non-idempotent)
- Status Code 201: Created (리소스 생성 성공)
- Location Header: 생성된 리소스의 URI 반환 (Best Practice)
"""

@router.post("", status_code=201)
def create_post(post: PostCreate) -> Dict:
    """
    게시글 생성 엔드포인트 (POST /posts)
    
    Args:
    - post (PostCreate): Pydantic이 파싱한 Request Body
    
    Returns:
    - Dict: 생성 메시지 + 생성된 게시글 데이터
    
    Status Code:
    - 201 Created: 리소스 생성 성공
    - 400 Bad Request: 잘못된 입력 데이터
    - 500 Internal Server Error: 서버 오류
    
    Note:
    - Pydantic으로 유효성 검증 완료된 데이터 전달
    - Controller의 create 메서드 호출
    - 내부 비즈니스 로직은 Controller가 담당 (id 자동 생성 등)
    - 예외 발생 시 FastAPI가 자동으로 500 Internal Server Error 반환
    """
    try:
        result = controller.create(
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            image_url=post.image_url
        )
        return {"message": "Created", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"게시글 생성 실패 - title: {post.title}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 생성 중 오류가 발생했습니다")



# ==================== READ ====================


@router.get("", status_code=200)
def get_all_posts() -> Dict:
    """
    전체 게시글 조회 엔드포인트 (GET /posts)
    
    Returns:
    - Dict: 성공 메시지 + 게시글 개수 + 전체 게시글 목록
    
    Status Code:
    - 200 OK: 조회 성공
    - 500 Internal Server Error: 서버 오류

    Note:
    - Controller의 get_all 메서드 호출
    - 내부 비즈니스 로직은 Controller가 담당 (실제 프로덕션에서는 페이징 등 구현)
    """

    try:
        posts = controller.get_all()
        return {
            "message": "Success",
            "count": len(posts),
            "data": posts
        }
    # 200 OK

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # 500 Internal Server Error


@router.get("/{post_id}")
def get_post(post_id: int) -> Dict:
    """
    특정 게시글 조회 엔드포인트 (GET /posts/{post_id})

    Args:
    - post_id (int): Path Parameter로 전달된 게시글 ID

    Returns:
    - Dict: 성공 메시지 + 조회된 게시글 데이터

    Status Code:
    - 200 OK: 조회 성공
    - 404 Not Found: 게시글이 존재하지 않음

    Note:
    - Controller에서 ValueError 발생 → HTTPException(404) 변환
    - increment_view=True로 조회수 자동 증가
    """
    try:
        post = controller.get_by_id(post_id, increment_view=True)
        return {"message": "Success", "data": post}
    # 200 OK

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found


# ==================== UPDATE ====================


@router.put("/{post_id}")
def update_post(post_id: int, post: PostCreate) -> Dict:
    """
    게시글 전체 교체 엔드포인트 (PUT /posts/{post_id})
    
    Args:
    - post_id (int): 수정할 게시글 ID
    - post (PostCreate): 새로운 게시글 데이터 (전체 필드 필수)
    
    Returns:
    - Dict: 수정 메시지 + 수정된 게시글 데이터
    
    Status Code:
    - 200 OK: 수정 성공
    - 404 Not Found: 게시글이 존재하지 않음
    """
    try:
        result = controller.update(post_id, post.title, post.content)
        return {"message": "Updated", "data": result}
    # 200 OK

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found


@router.patch("/{post_id}")
def partial_update_post(post_id: int, update_data: PostPartialUpdate) -> Dict:
    """
    게시글 부분 수정 엔드포인트 (PATCH /posts/{post_id})
    
    Args:
    - post_id (int): 수정할 게시글 ID
    - update_data (PostPartialUpdate): 수정할 필드들 (선택적)
    
    Returns:
    - Dict: 부분 수정 메시지 + 수정된 게시글 데이터
    
    Status Code:
    - 200 OK: 수정 성공
    - 404 Not Found: 게시글이 존재하지 않음
    
    Note:
    - exclude_unset=True: 클라이언트가 보내지 않은 필드는 None으로 유지
    """
    try:
        # Pydantic 모델에서 실제로 전송된 필드만 추출
        update_dict = update_data.model_dump(exclude_unset=True)
        
        result = controller.partial_update(
            post_id,
            title=update_dict.get("title"),
            content=update_dict.get("content")
        )
        return {"message": "Partially updated", "data": result}
    # 200 OK

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found



# ==================== DELETE ====================


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, user_id: int):
    """
    게시글 삭제 엔드포인트 (DELETE /posts/{post_id})

    Args:
    - post_id (int): 삭제할 게시글 ID
    - user_id (int): 사용자 ID (Query Parameter, 권한 확인용)

    Returns:
    - None (204 No Content)

    Status Code:
    - 204 No Content: 삭제 성공, 응답 본문 없음
    - 400 Bad Request: 권한 없음 (본인 게시글 아님)
    - 404 Not Found: 게시글이 존재하지 않음

    Note:
    - 본인이 작성한 게시글만 삭제 가능
    - 204는 본문이 없으므로 return 값 무시
    """
    try:
        # 게시글 존재 및 권한 확인
        post = controller.get_by_id(post_id, increment_view=False)
        if post["author_id"] != user_id:
            raise HTTPException(status_code=400, detail="본인이 작성한 게시글만 삭제할 수 있습니다")

        controller.delete(post_id)
        return None
    # 204 No Content

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found


# ==================== LIKE ====================


@router.post("/{post_id}/like")
def toggle_like(post_id: int, user_id: int) -> Dict:
    """
    좋아요 토글 엔드포인트 (POST /posts/{post_id}/like)

    Args:
    - post_id (int): 게시글 ID
    - user_id (int): 사용자 ID (Query Parameter)

    Returns:
    - Dict: 좋아요 토글 결과 + 업데이트된 게시글 데이터

    Status Code:
    - 200 OK: 좋아요 토글 성공
    - 404 Not Found: 게시글이 존재하지 않음

    Note:
    - 좋아요가 이미 있으면 취소, 없으면 추가
    """
    try:
        result = controller.toggle_like(post_id, user_id)
        action = "좋아요 추가" if result["liked"] else "좋아요 취소"
        return {
            "message": action,
            "data": result["post"],
            "liked": result["liked"]
        }
    # 200 OK

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found


@router.get("/{post_id}/is-liked")
def check_like_status(post_id: int, user_id: int) -> Dict:
    """
    좋아요 상태 확인 엔드포인트 (GET /posts/{post_id}/is-liked)

    Args:
    - post_id (int): 게시글 ID
    - user_id (int): 사용자 ID (Query Parameter)

    Returns:
    - Dict: 좋아요 상태

    Status Code:
    - 200 OK: 조회 성공

    Note:
    - 게시글이 존재하지 않아도 false 반환 (404 발생 안함)
    """
    try:
        # 게시글 존재 여부 확인
        controller.get_by_id(post_id, increment_view=False)
        is_liked = controller.is_liked_by_user(post_id, user_id)
        return {
            "message": "Success",
            "liked": is_liked
        }
    # 200 OK

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found


@router.delete("/{post_id}/like")
def cancel_like(post_id: int, user_id: int) -> Dict:
    """
    좋아요 취소 엔드포인트 (DELETE /posts/{post_id}/like)

    Args:
    - post_id (int): 게시글 ID
    - user_id (int): 사용자 ID (Query Parameter)

    Returns:
    - Dict: 좋아요 취소 결과 + 업데이트된 게시글 데이터

    Status Code:
    - 200 OK: 좋아요 취소 성공
    - 404 Not Found: 게시글이 존재하지 않음

    Note:
    - POST와 동일하게 토글 방식으로 동작
    - 좋아요가 있으면 취소, 없으면 추가
    """
    try:
        result = controller.toggle_like(post_id, user_id)
        action = "좋아요 추가" if result["liked"] else "좋아요 취소"
        return {
            "message": action,
            "data": result["post"],
            "liked": result["liked"]
        }
    # 200 OK

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 404 Not Found