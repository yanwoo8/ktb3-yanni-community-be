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
- GET /posts/{post_id}/comments: 특정 게시글의 댓글 목록 조회
- PUT /posts/{post_id}: 게시글 전체 수정
- PATCH /posts/{post_id}: 게시글 부분 수정
- DELETE /posts/{post_id}: 게시글 삭제
- POST /posts/{post_id}/like: 게시글 좋아요 토글
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.databases import get_db, SessionLocal
from app.models.post_model import PostModel
from app.models.user_model import UserModel
from app.models.comment_model import CommentModel
from app.controllers.post_controller import PostController
from app.controllers.user_controller import UserController
from app.controllers.comment_controller import CommentController
from app.schemas.post_schema import PostCreate, PostPartialUpdate
from app.services.ai_comment_service import get_ai_comment_service
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

    user_model = UserModel(db)
    post_model = PostModel(db)
    user_controller = UserController(user_model)
    return PostController(post_model, user_controller)


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



async def add_ai_comment_background(
    post_id: int,
    post_title: str,
    post_content: str
):
    """
    백그라운드 작업: AI 댓글 자동 생성 및 추가

    Args:
    - post_id: 게시글 ID
    - post_title: 게시글 제목
    - post_content: 게시글 내용

    Note:
    - 게시글 생성 후 비동기로 실행
    - AI 서비스 호출 및 댓글 생성
    - 자체 데이터베이스 세션 생성 (request session과 독립적)
    - 실패 시 로그 기록 (사용자에게는 영향 없음)
    """
    # 백그라운드 작업용 독립적인 DB 세션 생성
    db = SessionLocal()

    try:
        # AI 댓글 서비스 가져오기
        ai_service = get_ai_comment_service()

        # AI 댓글 생성 (비동기)
        ai_comment_content = await ai_service.generate_comment(post_title, post_content)

        # AI 봇 사용자 ID (사전에 생성된 AI 봇 계정 필요)
        # 없으면 관리자 계정(ID=1) 사용
        AI_BOT_USER_ID = 1  # TODO: AI 봇 전용 계정 생성

        # 댓글 컨트롤러 생성
        comment_model = CommentModel(db)
        user_model = UserModel(db)
        user_controller = UserController(user_model)
        post_model = PostModel(db)
        post_controller = PostController(post_model, user_controller)
        comment_controller = CommentController(comment_model, user_controller, post_controller)

        # AI 댓글 저장
        comment_controller.create(
            post_id=post_id,
            author_id=AI_BOT_USER_ID,
            content=ai_comment_content
        )

        logger.info(f"AI 댓글이 게시글 {post_id}에 성공적으로 추가되었습니다.")

    except Exception as e:
        logger.error(f"AI 댓글 생성 실패 (게시글 ID: {post_id}): {e}", exc_info=True)
        # 백그라운드 작업 실패는 사용자에게 영향을 주지 않음

    finally:
        # 세션을 반드시 닫아서 리소스 누수 방지
        db.close()







# ==================== CREATE ====================

@router.post("", status_code=201)
def create_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    controller: PostController = Depends(get_post_controller)
) -> Dict:
    """
    게시글 생성 엔드포인트 (POST /posts)

    Args:
    - post (PostCreate): 게시글 생성 요청 데이터
    - background_tasks (BackgroundTasks): FastAPI 백그라운드 작업
    - controller (PostController): 의존성 주입된 컨트롤러
>>>>>>> origin/main

    Returns:
    - Dict: 생성 메시지 + 게시글 데이터

    Status Code:
    - 201 Created: 생성 성공
    - 400 Bad Request: 작성자가 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - 게시글 생성 후 백그라운드에서 AI 댓글 자동 추가
    - AI 댓글 추가 실패는 사용자 응답에 영향 없음
    """
    try:
        result = controller.create(
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            image_url=post.image_url
        )

        # 백그라운드 작업: AI 댓글 추가
        background_tasks.add_task(
            add_ai_comment_background,
            post_id=result["id"],
            post_title=result["title"],
            post_content=result["content"]
        )


        # 백그라운드 작업: AI 댓글 추가
        background_tasks.add_task(
            add_ai_comment_background,
            post_id=result["id"],
            post_title=result["title"],
            post_content=result["content"]
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


@router.get("/{post_id}/comments", status_code=200)
def get_post_comments(
    post_id: int,
    controller: CommentController = Depends(get_comment_controller)
) -> Dict:
    """
    특정 게시글의 댓글 목록 조회 (GET /posts/{post_id}/comments)

    Args:
    - post_id (int): 게시글 ID
    - controller (CommentController): 의존성 주입된 컨트롤러

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

    except SQLAlchemyError as e:
        logger.error(f"댓글 목록 조회 실패 (DB 오류) - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"댓글 목록 조회 실패 - post_id: {post_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="댓글 조회 중 오류가 발생했습니다")


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
        # Safely extract optional fields without assigning back to the Pydantic model
        image_val = getattr(post, "image_url", None)
        if hasattr(post, "image_url"):
            # 간단한 유효성 검사: None(명시적 제거) 또는 문자열만 허용
            if image_val is not None and not isinstance(image_val, str):
                raise ValueError("image_url must be a string or null")
            # image_val == None 의 경우 이미지 제거 의도로 전달

        title_val = getattr(post, "title", None)
        content_val = getattr(post, "content", None)
     
        result = controller.partial_update(
            post_id,
            title=title_val,
            content=content_val,
            image_url=image_val
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
