"""
Development Routes (Database Version)

역할:
- 개발/테스트 환경에서만 사용하는 엔드포인트
- 데이터베이스 초기화 및 상태 조회 기능 제공

주의:
- 프로덕션 환경에서는 사용 금지
- 모든 데이터를 삭제하므로 신중히 사용

Endpoints:
- POST /dev/reset: 모든 데이터베이스 테이블 초기화
- GET /dev/status: 현재 데이터베이스 상태 조회
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

<<<<<<< HEAD
from app.databases import get_db, engine, Base
from app.databases.db_models import User, Post, Comment, post_likes
=======
from app.database import get_db, engine, Base
from app.db_models import User, Post, Comment, post_likes
>>>>>>> origin/main
import logging


# ==================== Router Setup ====================

router = APIRouter(
    prefix="/dev",
    tags=["development"]
)

logger = logging.getLogger(__name__)


# ==================== Reset Endpoint ====================

@router.post("/reset", status_code=200)
def reset_all_data(db: Session = Depends(get_db)) -> Dict:
    """
    모든 데이터베이스 초기화 엔드포인트 (POST /dev/reset)

    Args:
    - db (Session): 데이터베이스 세션

    Returns:
    - Dict: 초기화 성공 메시지

    Status Code:
    - 200 OK: 초기화 성공
    - 500 Internal Server Error: 서버 오류

    Note:
    - 개발/테스트 환경에서만 사용
    - 모든 User, Post, Comment, post_likes 데이터 삭제
    - 테이블은 유지되고 데이터만 삭제됨

    Warning:
    - 프로덕션 환경에서는 이 엔드포인트를 비활성화해야 함
    """
    try:
        # 순서 중요: 참조 무결성 위반을 피하기 위해 자식 → 부모 순으로 삭제
        # 1. 댓글 삭제 (Post와 User를 참조)
        deleted_comments = db.query(Comment).delete()

        # 2. 좋아요 삭제 (post_likes association table)
        deleted_likes = db.execute(post_likes.delete()).rowcount

        # 3. 게시글 삭제 (User를 참조)
        deleted_posts = db.query(Post).delete()

        # 4. 사용자 삭제 (참조되지 않음)
        deleted_users = db.query(User).delete()

        # 커밋
        db.commit()

        logger.info(f"데이터베이스 초기화 완료 - users: {deleted_users}, posts: {deleted_posts}, comments: {deleted_comments}, likes: {deleted_likes}")

        return {
            "message": "모든 데이터가 초기화되었습니다",
            "deleted": {
                "users": deleted_users,
                "posts": deleted_posts,
                "comments": deleted_comments,
                "likes": deleted_likes
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"데이터베이스 초기화 실패 (DB 오류) - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 초기화 중 오류가 발생했습니다")

    except Exception as e:
        db.rollback()
        logger.error(f"데이터베이스 초기화 실패 - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터 초기화 중 오류가 발생했습니다")


@router.get("/status", status_code=200)
def get_data_status(db: Session = Depends(get_db)) -> Dict:
    """
    현재 데이터베이스 상태 조회 엔드포인트 (GET /dev/status)

    Args:
    - db (Session): 데이터베이스 세션

    Returns:
    - Dict: 데이터 개수 정보

    Status Code:
    - 200 OK: 조회 성공
    - 500 Internal Server Error: 서버 오류
    """
    try:
        # 각 테이블의 레코드 수 조회
        user_count = db.query(User).count()
        post_count = db.query(Post).count()
        comment_count = db.query(Comment).count()

        # post_likes 테이블의 레코드 수 조회
        like_count = db.execute(post_likes.select()).fetchall()
        total_likes = len(like_count)

        return {
            "message": "현재 데이터베이스 상태",
            "data": {
                "users": user_count,
                "posts": post_count,
                "comments": comment_count,
                "total_likes": total_likes
            }
        }

    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 상태 조회 실패 (DB 오류) - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"데이터베이스 상태 조회 실패 - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="상태 조회 중 오류가 발생했습니다")
