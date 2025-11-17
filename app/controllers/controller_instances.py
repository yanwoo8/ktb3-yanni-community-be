"""
Controller Instances (Singleton Pattern with Model Layer)

역할:
- Route-Controller-Model 3계층 아키텍처 구현
- 전역에서 단일 인스턴스 공유 (Singleton Pattern)
- 의존성 주입을 통한 Controller 간 협력

설계 패턴:
- Singleton Pattern: 앱 전체에서 하나의 인스턴스만 생성
- Dependency Injection: Controller와 Model 간 의존성 주입
- Repository Pattern: Model을 통한 데이터 접근

아키텍처:
Route → Controller → Model → Data
- Route: HTTP 요청/응답 처리
- Controller: 비즈니스 로직
- Model: 데이터 접근 계층 (Repository)
- Data: In-memory 저장소 (List[Dict])

Note:
- 서버 재시작 시 데이터 소실 (In-memory 저장소)
- 프로덕션에서는 DB + ORM 사용 권장
"""

from app.models.user_model import UserModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.controllers.user_controller import UserController
from app.controllers.post_controller import PostController
from app.controllers.comment_controller import CommentController


# ==================== Model Instances ====================

# 1. UserModel 인스턴스 생성 (데이터 접근 계층)
user_model = UserModel()

# 2. PostModel 인스턴스 생성 (데이터 접근 계층)
post_model = PostModel()

# 3. CommentModel 인스턴스 생성 (데이터 접근 계층)
comment_model = CommentModel()


# ==================== Controller Instances ====================

# 1. UserController 인스턴스 생성 (비즈니스 로직 계층)
user_controller = UserController(user_model=user_model)

# 2. PostController 인스턴스 생성 (user_controller 의존성 주입)
post_controller = PostController(
    post_model=post_model,
    user_controller=user_controller
)

# 3. CommentController 인스턴스 생성 (user_controller, post_controller 의존성 주입)
comment_controller = CommentController(
    comment_model=comment_model,
    user_controller=user_controller,
    post_controller=post_controller
)


# ==================== Export ====================

__all__ = [
    "user_controller",
    "post_controller",
    "comment_controller",
    "user_model",      # auth_routes의 delete_user에서 사용
    "post_model",      # auth_routes의 delete_user에서 사용
    "comment_model"    # auth_routes의 delete_user에서 사용
]
