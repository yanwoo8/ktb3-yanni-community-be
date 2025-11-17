"""
Post Controller

역할:
1. 비즈니스 로직 처리: 게시글 CRUD + 좋아요/조회수 관리
2. Model 계층 호출: 데이터 접근은 PostModel에 위임
3. 예외 처리: 비즈니스 규칙 위반 시 예외 발생

설계 원칙:
- 단일 책임 원칙(SRP): 게시글 관련 비즈니스 로직만 담당
- 의존성 역전 원칙(DIP): HTTP 계층 및 데이터 계층과 독립적
- Repository 패턴: Model을 통한 데이터 접근

Note:
- Controller → Model → Data 계층 분리
- UserController 의존성: 작성자 정보 조회용
"""

from typing import List, Dict, Optional
from app.models.post_model import PostModel


class PostController:
    """
    게시글 비즈니스 로직을 담당하는 Controller

    Attributes:
    - post_model (PostModel): 게시글 데이터 접근 계층
    - user_controller: 사용자 정보 조회용 (의존성 주입)

    Methods:
    - create: 게시글 생성
    - get_all: 전체 게시글 조회
    - get_by_id: 특정 게시글 조회
    - update: 게시글 전체 교체
    - partial_update: 게시글 부분 수정
    - delete: 게시글 삭제
    - toggle_like: 좋아요 토글
    - is_liked_by_user: 좋아요 여부 확인
    - increment_comment_count: 댓글 수 증가
    - decrement_comment_count: 댓글 수 감소
    """

    def __init__(self, post_model: PostModel, user_controller=None):
        """
        Controller 초기화

        Args:
        - post_model (PostModel): 의존성 주입된 PostModel 인스턴스
        - user_controller: 작성자 정보 조회용 (선택)
        """
        self.post_model = post_model
        self.user_controller = user_controller


    # ==================== CREATE ====================

    def create(self, title: str, content: str, author_id: int,
               image_url: Optional[str] = None) -> Dict:
        """
        게시글 생성

        Args:
        - title (str): 제목
        - content (str): 내용
        - author_id (int): 작성자 ID
        - image_url (Optional[str]): 이미지 URL

        Returns:
        - Dict: 생성된 게시글 정보

        Raises:
        - ValueError: 작성자가 존재하지 않을 때

        Business Logic:
        - 작성자 정보 조회 (UserController)
        - 게시글 생성 (PostModel)
        """
        # 작성자 정보 조회
        if self.user_controller:
            author = self.user_controller.get_user_info(author_id)

            if not author:
                raise ValueError(f"작성자 ID {author_id}를 찾을 수 없습니다 - 작성자 정보: {author}")
            
            author_nickname = author["nickname"]
            author_profile_image = author.get("profile_image")

        else:
            author_nickname = "Unknown"
            author_profile_image = None

        # 게시글 생성 (Model에 위임)
        return self.post_model.create(

            title=title,
            content=content,
            author_id=author_id,
            author_nickname=author_nickname,
            author_profile_image=author_profile_image,
            image_url=image_url
        )


    # ==================== READ ====================

    def get_all(self) -> List[Dict]:
        """
        전체 게시글 조회 (최신순)

        Returns:
        - List[Dict]: 전체 게시글 목록
        """
        return self.post_model.find_all()


    def get_by_id(self, post_id: int, increment_view: bool = False) -> Dict:
        """
        특정 게시글 조회

        Args:
        - post_id (int): 게시글 ID
        - increment_view (bool): 조회수 증가 여부

        Returns:
        - Dict: 게시글 정보

        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        """
        post = self.post_model.find_by_id(post_id)

        if not post:
            raise ValueError(f"게시글 ID {post_id}가 존재하지 않습니다")
    
        # 조회수 증가
        if increment_view:
            self.post_model.increment_views(post_id)
            post = self.post_model.find_by_id(post_id)  # 업데이트된 정보 반환

        return post


    # ==================== UPDATE ====================

    def update(self, post_id: int, title: str, content: str,
               image_url: Optional[str] = None) -> Dict:
        """
        게시글 전체 교체 (PUT)

        Args:
        - post_id (int): 게시글 ID
        - title (str): 새 제목
        - content (str): 새 내용
        - image_url (Optional[str]): 새 이미지 URL

        Returns:
        - Dict: 수정된 게시글

        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        """
        updated_post = self.post_model.update(
            post_id,
            title=title,
            content=content,
            image_url=image_url
        )

        if not updated_post:
            raise ValueError(f"게시글 ID {post_id}가 존재하지 않습니다")

        return updated_post


    def partial_update(self, post_id: int, title: Optional[str] = None,
                       content: Optional[str] = None,
                       image_url: Optional[str] = None) -> Dict:
        """
        게시글 부분 수정 (PATCH)

        Args:
        - post_id (int): 게시글 ID
        - title (Optional[str]): 새 제목
        - content (Optional[str]): 새 내용
        - image_url (Optional[str]): 새 이미지 URL

        Returns:
        - Dict: 수정된 게시글

        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        """
        updated_post = self.post_model.update(
            post_id,
            title=title,
            content=content,
            image_url=image_url
        )

        if not updated_post:
            raise ValueError(f"게시글 ID {post_id}가 존재하지 않습니다")

        return updated_post


    # ==================== DELETE ====================

    def delete(self, post_id: int) -> None:
        """
        게시글 삭제

        Args:
        - post_id (int): 게시글 ID

        Raises:
        - ValueError: 게시글이 존재하지 않을 때

        Note:
        - 댓글은 comment_controller에서 CASCADE 삭제 처리
        """
        if not self.post_model.delete(post_id):
            raise ValueError(f"게시글 ID {post_id}가 존재하지 않습니다")


    # ==================== LIKE ====================

    def toggle_like(self, post_id: int, user_id: int) -> Dict:
        """
        좋아요 토글

        Args:
        - post_id (int): 게시글 ID
        - user_id (int): 사용자 ID

        Returns:
        - Dict: {"post": 업데이트된 게시글, "liked": 좋아요 상태}

        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        """
        result = self.post_model.toggle_like(post_id, user_id)

        if not result:
            raise ValueError(f"게시글 ID {post_id}가 존재하지 않습니다")

        post, liked = result
        return {"post": post, "liked": liked}


    def is_liked_by_user(self, post_id: int, user_id: int) -> bool:
        """
        사용자의 좋아요 여부 확인

        Args:
        - post_id (int): 게시글 ID
        - user_id (int): 사용자 ID

        Returns:
        - bool: 좋아요 여부
        """
        return self.post_model.is_liked_by_user(post_id, user_id)


    # ==================== COMMENT COUNT ====================

    def increment_comment_count(self, post_id: int) -> None:
        """
        댓글 수 증가

        Args:
        - post_id (int): 게시글 ID
        """
        self.post_model.increment_comment_count(post_id)


    def decrement_comment_count(self, post_id: int) -> None:
        """
        댓글 수 감소

        Args:
        - post_id (int): 게시글 ID
        """
        self.post_model.decrement_comment_count(post_id)
