"""
Comment Model (Database Repository)

역할:
1. 데이터 접근 계층: 댓글 데이터베이스와의 상호작용
2. CRUD 연산: 댓글 생성, 조회, 수정, 삭제
3. 관계 데이터 관리: 게시글별 댓글, 작성자별 댓글 조회

설계 원칙:
- Repository 패턴: 데이터 소스 추상화
- 단일 책임 원칙(SRP): 데이터 접근만 담당
- 참조 무결성: 게시글 삭제 시 댓글도 삭제 (CASCADE)

변경사항:
- In-memory List[Dict] → SQLAlchemy ORM (SQLite)
- CASCADE DELETE: ORM relationship으로 자동 처리
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.databases.db_models import Comment


class CommentModel:
    """
    댓글 데이터 접근 계층

    Attributes:
    - db (Session): SQLAlchemy 세션

    Methods:
    - create: 댓글 생성
    - find_by_id: ID로 댓글 조회
    - find_by_post: 게시글별 댓글 조회
    - find_by_author: 작성자별 댓글 조회
    - update: 댓글 수정
    - delete: 댓글 삭제
    - delete_by_post: 게시글의 모든 댓글 삭제
    - delete_by_author: 작성자의 모든 댓글 삭제
    """

    def __init__(self, db: Session):
        """
        Model 초기화

        Args:
        - db (Session): SQLAlchemy 세션 (의존성 주입)
        """
        self.db = db


    # ==================== CREATE ====================

    def create(self, post_id: int, author_id: int, content: str) -> Comment:
        """
        댓글 생성

        Args:
        - post_id (int): 게시글 ID
        - author_id (int): 작성자 ID
        - content (str): 댓글 내용

        Returns:
        - Comment: 생성된 댓글 ORM 객체

        Note:
        - author_nickname, author_profile_image는 relationship을 통해 자동 조회
        """
        new_comment = Comment(
            post_id=post_id,
            author_id=author_id,
            content=content
        )
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        return new_comment


    # ==================== READ ====================

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """
        ID로 댓글 조회

        Args:
        - comment_id (int): 댓글 ID

        Returns:
        - Optional[Comment]: 댓글 ORM 객체 (없으면 None)
        """
        return self.db.query(Comment).filter(Comment.id == comment_id).first()


    def find_by_post(self, post_id: int) -> list[Comment]:
        """
        게시글별 댓글 조회 (오래된 순)

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - list[Comment]: 댓글 ORM 객체 목록
        """
        return self.db.query(Comment)\
            .filter(Comment.post_id == post_id)\
            .order_by(Comment.created_at)\
            .all()


    def find_by_author(self, author_id: int) -> list[Comment]:
        """
        작성자별 댓글 조회

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - list[Comment]: 댓글 ORM 객체 목록
        """
        return self.db.query(Comment).filter(Comment.author_id == author_id).all()


    # ==================== UPDATE ====================

    def update(self, comment_id: int, content: str) -> Optional[Comment]:
        """
        댓글 수정

        Args:
        - comment_id (int): 댓글 ID
        - content (str): 새 댓글 내용

        Returns:
        - Optional[Comment]: 수정된 댓글 (없으면 None)
        """
        comment = self.find_by_id(comment_id)
        if not comment:
            return None

        comment.content = content
        self.db.commit()
        self.db.refresh(comment)
        return comment


    # ==================== DELETE ====================

    def delete(self, comment_id: int) -> bool:
        """
        댓글 삭제

        Args:
        - comment_id (int): 댓글 ID

        Returns:
        - bool: 삭제 성공 여부
        """
        comment = self.find_by_id(comment_id)
        if not comment:
            return False

        self.db.delete(comment)
        self.db.commit()
        return True


    def delete_by_post(self, post_id: int) -> int:
        """
        게시글의 모든 댓글 삭제 (CASCADE)

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - int: 삭제된 댓글 수
        """
        comments = self.find_by_post(post_id)
        count = len(comments)

        for comment in comments:
            self.db.delete(comment)

        self.db.commit()
        return count


    def delete_by_author(self, author_id: int) -> int:
        """
        작성자의 모든 댓글 삭제

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - int: 삭제된 댓글 수
        """
        comments = self.find_by_author(author_id)
        count = len(comments)

        for comment in comments:
            self.db.delete(comment)

        self.db.commit()
        return count
