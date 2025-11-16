"""
Comment Routes

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
"""

from typing import Dict, List
from fastapi import APIRouter, HTTPException
from app.schemas.comment_schema import CommentCreate, CommentUpdate
from app.controllers.controller_instances import comment_controller
import logging


# ==================== Router Setup ====================

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

# Controller 인스턴스 (공유 Singleton)
controller = comment_controller

# Logger 인스턴스 생성
logger = logging.getLogger(__name__)


# ==================== CREATE ====================

@router.post("", status_code=201)
def create_comment(comment: CommentCreate) -> Dict:
    """
    댓글 생성 엔드포인트 (POST /comments)

    Args:
    - comment (CommentCreate): Pydantic이 파싱한 Request Body
        - post_id: 게시글 ID
        - author_id: 작성자 ID
        - content: 댓글 내용

    Returns:
    - Dict: 생성 메시지 + 생성된 댓글 데이터

    Status Code:
    - 201 Created: 댓글 생성 성공
    - 400 Bad Request: 잘못된 입력 데이터
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.create(
            post_id=comment.post_id,
            author_id=comment.author_id,
            content=comment.content
        )
        return {"message": "Created", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"댓글 생성 실패 - post_id: {comment.post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="댓글 생성 중 오류가 발생했습니다")


# ==================== READ ====================

@router.get("/post/{post_id}")
def get_comments_by_post(post_id: int) -> Dict:
    """
    특정 게시글의 댓글 목록 조회 (GET /comments/post/{post_id})

    Args:
    - post_id (int): 게시글 ID

    Returns:
    - Dict: 성공 메시지 + 댓글 개수 + 댓글 목록

    Status Code:
    - 200 OK: 조회 성공
    - 500 Internal Server Error: 서버 오류
    """
    try:
        comments = controller.get_by_post_id(post_id)
        return {
            "message": "Success",
            "count": len(comments),
            "data": comments
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{comment_id}")
def get_comment(comment_id: int) -> Dict:
    """
    특정 댓글 조회 (GET /comments/{comment_id})

    Args:
    - comment_id (int): 댓글 ID

    Returns:
    - Dict: 성공 메시지 + 댓글 데이터

    Status Code:
    - 200 OK: 조회 성공
    - 404 Not Found: 댓글이 존재하지 않음
    """
    try:
        comment = controller.get_by_id(comment_id)
        return {"message": "Success", "data": comment}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== UPDATE ====================

@router.put("/{comment_id}")
def update_comment(comment_id: int, update_data: CommentUpdate, user_id: int) -> Dict:
    """
    댓글 수정 (PUT /comments/{comment_id})

    Args:
    - comment_id (int): 댓글 ID
    - update_data (CommentUpdate): 수정할 댓글 내용
    - user_id (int): 수정 요청 사용자 ID (Query Parameter)

    Returns:
    - Dict: 수정 메시지 + 수정된 댓글 데이터

    Status Code:
    - 200 OK: 수정 성공
    - 400 Bad Request: 권한 없음
    - 404 Not Found: 댓글이 존재하지 않음
    """
    try:
        result = controller.update(
            comment_id=comment_id,
            content=update_data.content,
            user_id=user_id
        )
        return {"message": "Updated", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== DELETE ====================

@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, user_id: int):
    """
    댓글 삭제 (DELETE /comments/{comment_id})

    Args:
    - comment_id (int): 댓글 ID
    - user_id (int): 삭제 요청 사용자 ID (Query Parameter)

    Returns:
    - None (204 No Content)

    Status Code:
    - 204 No Content: 삭제 성공
    - 400 Bad Request: 권한 없음
    - 404 Not Found: 댓글이 존재하지 않음
    """
    try:
        controller.delete(comment_id=comment_id, user_id=user_id)
        return None

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
