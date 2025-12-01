"""
ORM Database Models

역할:
1. 데이터베이스 테이블 정의 (SQLAlchemy ORM)
2. 테이블 간 관계 설정 (Foreign Key, Relationship)
3. 데이터 무결성 제약 조건 정의

설계 원칙:
- ORM (Object-Relational Mapping): 클래스 = 테이블
- 참조 무결성: Foreign Key Constraint
- CASCADE: 부모 삭제 시 자식도 자동 삭제

테이블 구조:
1. users: 사용자 정보
2. posts: 게시글 정보
3. comments: 댓글 정보
4. post_likes: 게시글 좋아요 (다대다 관계)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.databases import Base


# ==================== Association Table (다대다 관계) ====================

post_likes = Table(
    'post_likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
)
"""
게시글 좋아요 연결 테이블 (Association Table)

관계:
- 한 사용자는 여러 게시글에 좋아요 가능
- 한 게시글은 여러 사용자로부터 좋아요 받을 수 있음

구조:
- user_id: 사용자 ID (복합 기본키)
- post_id: 게시글 ID (복합 기본키)
- ondelete='CASCADE': 사용자/게시글 삭제 시 좋아요도 자동 삭제
"""


# ==================== User Model ====================

class User(Base):
    """
    사용자 테이블

    Columns:
    - id: 기본키 (자동 증가)
    - email: 이메일 (고유, 필수)
    - password: 비밀번호 (해시화된 값)
    - nickname: 닉네임 (고유, 필수)
    - profile_image: 프로필 이미지 URL
    - created_at: 생성 시각 (자동 설정)

    Relationships:
    - posts: 작성한 게시글 목록 (1:N, CASCADE DELETE)
    - comments: 작성한 댓글 목록 (1:N, CASCADE DELETE)
    - liked_posts: 좋아요한 게시글 목록 (N:M)
    """
    __tablename__ = "users"

    # Columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(10), unique=True, nullable=False, index=True)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",  # 사용자 삭제 시 게시글도 삭제
        passive_deletes=True
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",  # 사용자 삭제 시 댓글도 삭제
        passive_deletes=True
    )
    liked_posts = relationship(
        "Post",
        secondary=post_likes,
        back_populates="liked_by_users"
    )


# ==================== Post Model ====================

class Post(Base):
    """
    게시글 테이블

    Columns:
    - id: 기본키 (자동 증가)
    - title: 제목 (필수)
    - content: 내용 (필수)
    - image_url: 게시글 이미지 URL
    - author_id: 작성자 ID (외래키, 필수)
    - views: 조회수 (기본값 0)
    - created_at: 생성 시각 (자동 설정)

    Relationships:
    - author: 작성자 정보 (N:1)
    - comments: 댓글 목록 (1:N, CASCADE DELETE)
    - liked_by_users: 좋아요한 사용자 목록 (N:M)

    Computed Fields:
    - likes: 좋아요 수 (liked_by_users 길이)
    - comment_count: 댓글 수 (comments 길이)
    """
    __tablename__ = "posts"

    # Columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    author_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    views = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",  # 게시글 삭제 시 댓글도 삭제
        passive_deletes=True
    )
    liked_by_users = relationship(
        "User",
        secondary=post_likes,
        back_populates="liked_posts"
    )


# ==================== Comment Model ====================

class Comment(Base):
    """
    댓글 테이블

    Columns:
    - id: 기본키 (자동 증가)
    - content: 댓글 내용 (필수)
    - author_id: 작성자 ID (외래키, 필수)
    - post_id: 게시글 ID (외래키, 필수)
    - created_at: 생성 시각 (자동 설정)

    Relationships:
    - author: 작성자 정보 (N:1)
    - post: 게시글 정보 (N:1)
    """
    __tablename__ = "comments"

    # Columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)
    author_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    post_id = Column(
        Integer,
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
