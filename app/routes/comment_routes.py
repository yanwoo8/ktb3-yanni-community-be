"""
Comment Routes (Database Version)

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
- POST /comments: 댓글 생성
- GET /comments/{comment_id}: 특정 댓글 조회
- PUT /comments/{comment_id}: 댓글 수정
- DELETE /comments/{comment_id}: 댓글 삭제

Dependencies:
- get_comment_controller [CommentController] Depends on get_db [Session]
    - create_comment (POST /comments) Depends on get_comment_controller
    - get_comment (GET /comments/{comment_id}) Depends on get_comment_controller
    - update_comment (PUT /comments/{comment_id}) Depends on get_comment_controller
    - delete_comment (DELETE /comments/{comment_id}) Depends on get_comment_controller
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.databases import get_db
from app.models.comment_model import CommentModel
from app.models.user_model import UserModel
from app.models.post_model import PostModel
from app.controllers.comment_controller import CommentController
from app.controllers.user_controller import UserController
from app.controllers.post_controller import PostController
from app.schemas.comment_schema import CommentCreate, CommentUpdate
from app.utils.dependencies import get_current_user
import logging


# ==================== Router Setup ====================

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

logger = logging.getLogger(__name__)


# ==================== Helper Functions ====================

def get_comment_controller(db: Session = Depends(get_db)) -> CommentController:
    """
    CommentController 의존성 주입 함수

    Args:
    - db (Session): 데이터베이스 세션

    Returns:
    - CommentController: 댓글 컨트롤러 인스턴스
    """
    comment_model = CommentModel(db)
    user_model = UserModel(db)
    post_model = PostModel(db)
    user_controller = UserController(user_model)
    post_controller = PostController(post_model, user_controller)
    return CommentController(comment_model, user_controller, post_controller)






# ==================== CREATE ====================

@router.post("", status_code=201)
def create_comment(
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user),
    controller: CommentController = Depends(get_comment_controller)
) -> Dict:
    """
    댓글 생성 엔드포인트 (POST /comments)

    Args:
    - comment (CommentCreate): 댓글 생성 요청 데이터 (post_id, content)
    - current_user (dict): JWT 토큰에서 추출한 현재 로그인 사용자 정보
    - controller (CommentController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 생성 메시지 + 댓글 데이터

    Status Code:
    - 201 Created: 생성 성공
    - 401 Unauthorized: 인증되지 않은 사용자
    - 400 Bad Request: 게시글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - JWT 인증 필수: Authorization 헤더에 Bearer 토큰 필요
    - author_id는 토큰에서 자동 추출 (요청 바디에 포함 불필요)

    Example Request:
    ```
    POST /comments
    Headers:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Body:
        {
            "post_id": 1,
            "content": "댓글 내용"
        }
    ```
    """
    # JWT 토큰에서 추출한 사용자 ID를 author_id로 사용
    author_id = current_user["id"]

    try:
        result = controller.create(
            post_id=comment.post_id,
            author_id=author_id,
            content=comment.content
        )
        return {"message": "Created", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"댓글 생성 실패 (DB 오류) - post_id: {comment.post_id}, author_id: {author_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"댓글 생성 실패 - post_id: {comment.post_id}, author_id: {author_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="댓글 생성 중 오류가 발생했습니다")


# ==================== READ ====================

@router.get("/{comment_id}", status_code=200)
def get_comment(
    comment_id: int,
    controller: CommentController = Depends(get_comment_controller)
) -> Dict:
    """
    특정 댓글 조회 (GET /comments/{comment_id})

    Args:
    - comment_id (int): 댓글 ID
    - controller (CommentController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 성공 메시지 + 댓글 데이터

    Status Code:
    - 200 OK: 조회 성공
    - 404 Not Found: 댓글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류
    """
    try:
        comment = controller.get_by_id(comment_id)
        return {"message": "Success", "data": comment}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"댓글 조회 실패 (DB 오류) - comment_id: {comment_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"댓글 조회 실패 - comment_id: {comment_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="댓글 조회 중 오류가 발생했습니다")


# ==================== UPDATE ====================

@router.put("/{comment_id}", status_code=200)
def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    user_id: int,
    controller: CommentController = Depends(get_comment_controller)
) -> Dict:
    """
    댓글 수정 (PUT /comments/{comment_id})

    Args:
    - comment_id (int): 댓글 ID
    - update_data (CommentUpdate): 수정할 댓글 내용
    - user_id (int): 수정 요청 사용자 ID (Query Parameter)
    - controller (CommentController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 수정 메시지 + 수정된 댓글 데이터

    Status Code:
    - 200 OK: 수정 성공
    - 400 Bad Request: 권한 없음
    - 404 Not Found: 댓글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.update(
            comment_id=comment_id,
            content=update_data.content,
            user_id=user_id
        )
        return {"message": "Updated", "data": result}

    except ValueError as e:
        # 댓글이 존재하지 않는 경우는 404, 권한 없는 경우는 400
        if "존재하지 않습니다" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"댓글 수정 실패 (DB 오류) - comment_id: {comment_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"댓글 수정 실패 - comment_id: {comment_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="댓글 수정 중 오류가 발생했습니다")


# ==================== DELETE ====================

@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    user_id: int,
    controller: CommentController = Depends(get_comment_controller)
):
    """
    댓글 삭제 (DELETE /comments/{comment_id})

    Args:
    - comment_id (int): 댓글 ID
    - user_id (int): 삭제 요청 사용자 ID (Query Parameter)
    - controller (CommentController): 의존성 주입된 컨트롤러

    Returns:
    - None (204 No Content)

    Status Code:
    - 204 No Content: 삭제 성공
    - 400 Bad Request: 권한 없음
    - 404 Not Found: 댓글이 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - 작성자만 삭제 가능
    - 게시글의 댓글수는 ORM relationship으로 자동 계산
    """
    try:
        controller.delete(comment_id=comment_id, user_id=user_id)
        return None

    except ValueError as e:
        # 댓글이 존재하지 않는 경우는 404, 권한 없는 경우는 400
        if "존재하지 않습니다" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"댓글 삭제 실패 (DB 오류) - comment_id: {comment_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"댓글 삭제 실패 - comment_id: {comment_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="댓글 삭제 중 오류가 발생했습니다")
