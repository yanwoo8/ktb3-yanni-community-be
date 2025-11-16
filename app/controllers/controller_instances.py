"""
Controller Instances (Singleton Pattern)

역할:
- 전역에서 단일 Controller 인스턴스를 공유하기 위한 모듈
- 각 라우트에서 동일한 Controller 인스턴스를 사용하여 데이터 공유

설계 패턴:
- Singleton Pattern: 앱 전체에서 하나의 인스턴스만 생성
- Dependency Injection: 라우트에서 이 인스턴스를 주입받아 사용

Note:
- 서버 재시작 시 데이터 소실 (In-memory 저장소)
- 프로덕션에서는 DB + Repository 패턴 사용 권장
"""

from app.controllers.user_controller import UserController
from app.controllers.post_controller import PostController
from app.controllers.comment_controller import CommentController


# ==================== Singleton Instances ====================

# 1. UserController 인스턴스 생성
user_controller = UserController()

# 2. PostController 인스턴스 생성 (user_controller 의존성 주입)
post_controller = PostController(user_controller=user_controller)

# 3. CommentController 인스턴스 생성 (user_controller, post_controller 의존성 주입)
comment_controller = CommentController(
    user_controller=user_controller,
    post_controller=post_controller
)


# ==================== Export ====================

__all__ = [
    "user_controller",
    "post_controller",
    "comment_controller"
]
