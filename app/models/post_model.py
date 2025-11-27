"""
Post Model (Database Repository)

역할:
1. 데이터 접근 계층: 게시글 데이터베이스와의 상호작용
2. CRUD 연산: 게시글 생성, 조회, 수정, 삭제
3. 관계 데이터 관리: 좋아요, 조회수, 댓글 수 추적

설계 원칙:
- Repository 패턴: 데이터 소스 추상화
- 단일 책임 원칙(SRP): 데이터 접근만 담당
- 의존성 주입: SQLAlchemy Session 주입

변경사항:
- In-memory List[Dict] → SQLAlchemy ORM (SQLite)
- 좋아요: dict 추적 → post_likes 테이블 (다대다 관계)
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db_models import Post, User


class PostModel:
    """
    게시글 데이터 접근 계층

    Attributes:
    - db (Session): SQLAlchemy 세션

    Methods:
    - create: 게시글 생성
    - find_by_id: ID로 게시글 조회
    - find_all: 전체 게시글 조회
    - find_by_author: 작성자별 게시글 조회
    - update: 게시글 수정
    - delete: 게시글 삭제
    - delete_by_author: 특정 작성자의 모든 게시글 삭제
    - increment_views: 조회수 증가
    - toggle_like: 좋아요 토글
    - is_liked_by_user: 사용자의 좋아요 여부 확인
    """

    def __init__(self, db: Session):
        """
        Model 초기화

        Args:
        - db (Session): SQLAlchemy 세션 (의존성 주입)
        """
        self.db = db


    # ==================== CREATE ====================

    def create(self, title: str, content: str, author_id: int,
               image_url: Optional[str] = None) -> Post:
        """
        게시글 생성

        Args:
        - title (str): 제목
        - content (str): 내용
        - author_id (int): 작성자 ID
        - image_url (Optional[str]): 게시글 이미지 URL

        Returns:
        - Post: 생성된 게시글 ORM 객체

        Note:
        - author_nickname, author_profile_image는 relationship을 통해 자동 조회
        """
        new_post = Post(
            title=title,
            content=content,
            image_url=image_url,
            author_id=author_id
        )
        self.db.add(new_post)
        self.db.commit()
        self.db.refresh(new_post)
        return new_post


    # ==================== READ ====================

    def find_by_id(self, post_id: int) -> Optional[Post]:
        """
        ID로 게시글 조회

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - Optional[Post]: 게시글 ORM 객체 (없으면 None)
        """
        return self.db.query(Post).filter(Post.id == post_id).first()


    def find_all(self) -> list[Post]:
        """
        전체 게시글 조회 (최신순 정렬)

        Returns:
        - list[Post]: 전체 게시글 ORM 객체 목록
        """
        return self.db.query(Post).order_by(desc(Post.created_at)).all()


    def find_by_author(self, author_id: int) -> list[Post]:
        """
        작성자별 게시글 조회

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - list[Post]: 해당 작성자의 게시글 목록
        """
        return self.db.query(Post).filter(Post.author_id == author_id).all()


    # ==================== UPDATE ====================

    def update(self, post_id: int, **kwargs) -> Optional[Post]:
        """
        게시글 수정

        Args:
        - post_id (int): 게시글 ID
        - **kwargs: 수정할 필드들 (title, content, image_url)

        Returns:
        - Optional[Post]: 수정된 게시글 (없으면 None)
        """
        post = self.find_by_id(post_id)
        if not post:
            return None

        # 수정 불가 필드
        immutable_fields = {"id", "author_id", "created_at", "views"}

        for key, value in kwargs.items():
            if key not in immutable_fields and hasattr(post, key) and value is not None:
                setattr(post, key, value)

        self.db.commit()
        self.db.refresh(post)
        return post


    def increment_views(self, post_id: int) -> bool:
        """
        조회수 증가

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - bool: 성공 여부
        """
        post = self.find_by_id(post_id)
        if not post:
            return False

        post.views += 1
        self.db.commit()
        return True


    # ==================== LIKE ====================

    def toggle_like(self, post_id: int, user_id: int) -> Optional[tuple[Post, bool]]:
        """
        좋아요 토글

        Args:
        - post_id (int): 게시글 ID
        - user_id (int): 사용자 ID

        Returns:
        - Optional[tuple[Post, bool]]: (업데이트된 게시글, 좋아요 상태)
            - True: 좋아요 추가
            - False: 좋아요 취소
        """
        post = self.find_by_id(post_id)
        user = self.db.query(User).filter(User.id == user_id).first()

        if not post or not user:
            return None

        # 이미 좋아요한 경우
        if user in post.liked_by_users:
            post.liked_by_users.remove(user)
            self.db.commit()
            self.db.refresh(post)
            return (post, False)
        else:
            post.liked_by_users.append(user)
            self.db.commit()
            self.db.refresh(post)
            return (post, True)


    def is_liked_by_user(self, post_id: int, user_id: int) -> bool:
        """
        사용자의 좋아요 여부 확인

        Args:
        - post_id (int): 게시글 ID
        - user_id (int): 사용자 ID

        Returns:
        - bool: 좋아요 여부
        """
        post = self.find_by_id(post_id)
        user = self.db.query(User).filter(User.id == user_id).first()

        if not post or not user:
            return False

        return user in post.liked_by_users


    # ==================== DELETE ====================

    def delete(self, post_id: int) -> bool:
        """
        게시글 삭제

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - bool: 삭제 성공 여부

        Note:
        - CASCADE DELETE: 댓글, 좋아요도 자동 삭제 (ORM 설정)
        """
        post = self.find_by_id(post_id)
        if not post:
            return False

        self.db.delete(post)
        self.db.commit()
        return True


    def delete_by_author(self, author_id: int) -> list[int]:
        """
        특정 작성자의 모든 게시글 삭제

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - list[int]: 삭제된 게시글 ID 목록
        """
        posts = self.find_by_author(author_id)
        deleted_ids = [post.id for post in posts]

        for post in posts:
            self.db.delete(post)

        self.db.commit()
        return deleted_ids
