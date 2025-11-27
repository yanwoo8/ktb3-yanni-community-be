"""
Post Routes (Database Version)

역할:
1. HTTP 요청/응답 처리: Request → Controller → Response
2. 상태 코드 매핑: Controller 예외 → HTTP Status Code
3. 경로 라우팅: URL 패턴 정의
4. 데이터베이스 세션 관리: Dependency Injection

설계 원칙:
- 얇은 계층(Thin Layer): 비즈니스 로직은 Controller에 위임
- 단일 책임 원칙(SRP): HTTP 계층만 담당
- 의존성 주입: DB Session → Model → Controller

Endpoints:
- POST /posts: 게시글 생성
- GET /posts: 전체 게시글 조회
- GET /posts/{post_id}: 특정 게시글 조회
- PUT /posts/{post_id}: 게시글 전체 수정
- PATCH /posts/{post_id}: 게시글 부분 수정
- DELETE /posts/{post_id}: 게시글 삭제
- POST /posts/{post_id}/like: 게시글 좋아요 토글
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.post_model import PostModel
from app.models.user_model import UserModel
from app.controllers.post_controller import PostController
from app.controllers.user_controller import UserController
from app.schemas.post_schema import PostCreate, PostPartialUpdate
import logging


# ==================== Router Setup ====================

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

logger = logging.getLogger(__name__)


# ==================== Helper Functions ====================

def get_post_controller(db: Session = Depends(get_db)) -> PostController:
    """
    PostController 의존성 주입 함수

    Args:
    - db (Session): 데이터베이스 세션

    Returns:
    - PostController: 게시글 컨트롤러 인스턴스
    """
    post_model = PostModel(db)
    user_model = UserModel(db)
    user_controller = UserController(user_model)
    return PostController(post_model, user_controller)


# ==================== CREATE ====================

@router.post("", status_code=201)
def create_post(
    post: PostCreate,
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    게시글 생성 엔드포인트 (POST /posts)

    Args:
    - post (PostCreate): 게시글 생성 요청 데이터
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 생성 메시지 + 게시글 데이터

    Status Code:
    - 201 Created: 생성 성공
    - 400 Bad Request: 작성자가 존재하지 않음
    - 500 Internal Server Error: 서버 오류
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

    except SQLAlchemyError as e:
        logger.error(f"게시글 생성 실패 (DB 오류) - author_id: {post.author_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"게시글 생성 실패 - author_id: {post.author_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 생성 중 오류가 발생했습니다")


# ==================== READ ====================

@router.get("", status_code=200)
def get_all_posts(
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    전체 게시글 조회 엔드포인트 (GET /posts)

    Args:
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 전체 게시글 목록 (최신순)

    Status Code:
    - 200 OK: 조회 성공
    - 500 Internal Server Error: 서버 오류
    """
    try:
        posts = controller.get_all()
        return {"message": "Success", "data": posts, "count": len(posts)}

    except SQLAlchemyError as e:
        logger.error(f"게시글 목록 조회 실패 (DB 오류) - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"게시글 목록 조회 실패 - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 조회 중 오류가 발생했습니다")


@router.get("/{post_id}", status_code=200)
def get_post_by_id(
    post_id: int,
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    특정 게시글 조회 엔드포인트 (GET /posts/{post_id})

    Args:
    - post_id (int): 게시글 ID
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 게시글 데이터

    Status Code:
    - 200 OK: 조회 성공
    - 404 Not Found: 게시글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - 조회수 자동 증가
    """
    try:
        post = controller.get_by_id(post_id, increment_view=True)
        return {"message": "Success", "data": post}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"게시글 조회 실패 (DB 오류) - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"게시글 조회 실패 - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 조회 중 오류가 발생했습니다")


# ==================== UPDATE ====================

@router.put("/{post_id}", status_code=200)
def update_post(
    post_id: int,
    post: PostCreate,
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    게시글 전체 교체 엔드포인트 (PUT /posts/{post_id})

    Args:
    - post_id (int): 게시글 ID
    - post (PostCreate): 새 게시글 데이터
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 수정된 게시글 데이터

    Status Code:
    - 200 OK: 수정 성공
    - 404 Not Found: 게시글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.update(
            post_id,
            title=post.title,
            content=post.content,
            image_url=post.image_url
        )
        return {"message": "Updated", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"게시글 수정 실패 (DB 오류) - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"게시글 수정 실패 - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 수정 중 오류가 발생했습니다")


@router.patch("/{post_id}", status_code=200)
def partial_update_post(
    post_id: int,
    post: PostPartialUpdate,
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    게시글 부분 수정 엔드포인트 (PATCH /posts/{post_id})

    Args:
    - post_id (int): 게시글 ID
    - post (PostPartialUpdate): 수정할 필드들
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 수정된 게시글 데이터

    Status Code:
    - 200 OK: 수정 성공
    - 404 Not Found: 게시글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.partial_update(
            post_id,
            title=post.title,
            content=post.content,
            image_url=post.image_url
        )
        return {"message": "Updated", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"게시글 부분 수정 실패 (DB 오류) - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"게시글 부분 수정 실패 - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 수정 중 오류가 발생했습니다")


# ==================== DELETE ====================

@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    controller: PostController = Depends(get_post_controller)
):
    """
    게시글 삭제 엔드포인트 (DELETE /posts/{post_id})

    Args:
    - post_id (int): 게시글 ID
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - None (204 No Content)

    Status Code:
    - 204 No Content: 삭제 성공
    - 404 Not Found: 게시글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - CASCADE DELETE: 댓글, 좋아요도 자동 삭제 (데이터베이스 제약)
    """
    try:
        controller.delete(post_id)
        return None

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"게시글 삭제 실패 (DB 오류) - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"게시글 삭제 실패 - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="게시글 삭제 중 오류가 발생했습니다")


# ==================== LIKE ====================

@router.post("/{post_id}/like", status_code=200)
def toggle_like(
    post_id: int,
    user_id: int,
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    게시글 좋아요 토글 엔드포인트 (POST /posts/{post_id}/like)

    Args:
    - post_id (int): 게시글 ID
    - user_id (int): 사용자 ID (쿼리 파라미터)
    - controller (PostController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 업데이트된 게시글 + 좋아요 상태

    Status Code:
    - 200 OK: 성공
    - 404 Not Found: 게시글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.toggle_like(post_id, user_id)
        message = "좋아요 추가" if result["liked"] else "좋아요 취소"
        return {"message": message, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"좋아요 토글 실패 (DB 오류) - post_id: {post_id}, user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"좋아요 토글 실패 - post_id: {post_id}, user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="좋아요 처리 중 오류가 발생했습니다")
