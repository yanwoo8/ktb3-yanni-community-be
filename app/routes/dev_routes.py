"""
Development Routes

역할:
- 개발/테스트 환경에서만 사용하는 엔드포인트
- 데이터 리셋 기능 제공

주의:
- 프로덕션 환경에서는 사용 금지
- 모든 데이터를 삭제하므로 신중히 사용

Endpoints:
- POST /dev/reset: 모든 데이터 초기화
- GET /dev/status: 현재 데이터 상태 조회
"""

from typing import Dict
from fastapi import APIRouter
from app.controllers.controller_instances import user_model, post_model, comment_model


# ==================== Router Setup ====================

router = APIRouter(
    prefix="/dev",
    tags=["development"]
)


# ==================== Reset Endpoint ====================

@router.post("/reset", status_code=200)
def reset_all_data() -> Dict:
    """
    모든 데이터 초기화 엔드포인트 (POST /dev/reset)

    Returns:
    - Dict: 초기화 성공 메시지

    Status Code:
    - 200 OK: 초기화 성공

    Note:
    - 개발/테스트 환경에서만 사용
    - 모든 User, Post, Comment 데이터 삭제
    - 좋아요 정보도 모두 삭제

    Warning:
    - 프로덕션 환경에서는 이 엔드포인트를 비활성화해야 함
    """
    # User 데이터 초기화
    user_model.users.clear()
    user_model._next_id = 1  # ID 카운터 리셋

    # Post 데이터 초기화
    post_model.posts.clear()
    post_model.user_likes.clear()
    post_model._next_id = 1  # ID 카운터 리셋

    # Comment 데이터 초기화
    comment_model.comments.clear()
    comment_model._next_id = 1  # ID 카운터 리셋

    return {
        "message": "모든 데이터가 초기화되었습니다",
        "reset": {
            "users": "cleared",
            "posts": "cleared",
            "comments": "cleared",
            "likes": "cleared"
        }
    }


@router.get("/status", status_code=200)
def get_data_status() -> Dict:
    """
    현재 데이터 상태 조회 엔드포인트 (GET /dev/status)

    Returns:
    - Dict: 데이터 개수 정보

    Status Code:
    - 200 OK: 조회 성공
    """
    return {
        "message": "현재 데이터 상태",
        "data": {
            "users": len(user_model.users),
            "posts": len(post_model.posts),
            "comments": len(comment_model.comments),
            "total_likes": sum(len(likes) for likes in post_model.user_likes.values())
        }
    }
