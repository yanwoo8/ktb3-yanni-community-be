"""
User Model (Database Repository)

역할:
1. 데이터 접근 계층 (Data Access Layer): 데이터베이스와의 상호작용
2. CRUD 연산: 사용자 데이터 생성, 조회, 수정, 삭제
3. 데이터 무결성: 중복 검증, 존재 여부 확인

설계 원칙:
- Repository 패턴: 데이터 소스 추상화
- 단일 책임 원칙(SRP): 데이터 접근만 담당
- 의존성 주입: SQLAlchemy Session 주입

변경사항:
- In-memory List[Dict] → SQLAlchemy ORM (SQLite)
- 트랜잭션 관리: commit/rollback 자동 처리
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.databases.db_models import User


class UserModel:
    """
    사용자 데이터 접근 계층

    Attributes:
    - db (Session): SQLAlchemy 세션

    Methods:
    - create: 사용자 생성
    - find_by_id: ID로 사용자 조회
    - find_by_email: 이메일로 사용자 조회
    - find_by_nickname: 닉네임으로 사용자 조회
    - find_all: 전체 사용자 조회
    - update: 사용자 정보 수정
    - delete: 사용자 삭제
    """

    def __init__(self, db: Session):
        """
        Model 초기화

        Args:
        - db (Session): SQLAlchemy 세션 (의존성 주입)
        """
        self.db = db


    # ==================== CREATE ====================

    def create(self, email: str, password: str, nickname: str,
               profile_image: Optional[str] = None) -> User:
        """
        사용자 생성

        Args:
        - email (str): 이메일
        - password (str): 비밀번호 (해시화된 값)
        - nickname (str): 닉네임
        - profile_image (Optional[str]): 프로필 이미지 URL

        Returns:
        - User: 생성된 사용자 ORM 객체

        Raises:
        - IntegrityError: 이메일/닉네임 중복 시 (UNIQUE 제약 위반)
        """
        try:
            new_user = User(
                email=email,
                password=password,
                nickname=nickname,
                profile_image=profile_image
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)  # DB에서 생성된 값(id, created_at) 가져오기
            return new_user
        except IntegrityError:
            self.db.rollback()
            raise


    # ==================== READ ====================

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        ID로 사용자 조회

        Args:
        - user_id (int): 사용자 ID

        Returns:
        - Optional[User]: 사용자 ORM 객체 (없으면 None)
        """
        return self.db.query(User).filter(User.id == user_id).first()


    def find_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회

        Args:
        - email (str): 이메일

        Returns:
        - Optional[User]: 사용자 ORM 객체 (없으면 None)
        """
        return self.db.query(User).filter(User.email == email).first()


    def find_by_nickname(self, nickname: str) -> Optional[User]:
        """
        닉네임으로 사용자 조회

        Args:
        - nickname (str): 닉네임

        Returns:
        - Optional[User]: 사용자 ORM 객체 (없으면 None)
        """
        return self.db.query(User).filter(User.nickname == nickname).first()


    def find_all(self) -> list[User]:
        """
        전체 사용자 조회

        Returns:
        - list[User]: 전체 사용자 ORM 객체 목록
        """
        return self.db.query(User).all()


    # ==================== UPDATE ====================

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """
        사용자 정보 수정

        Args:
        - user_id (int): 사용자 ID
        - **kwargs: 수정할 필드들 (nickname, profile_image 등)

        Returns:
        - Optional[User]: 수정된 사용자 ORM 객체 (없으면 None)

        Raises:
        - IntegrityError: 닉네임 중복 시
        """
        user = self.find_by_id(user_id)
        if not user:
            return None

        try:
            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)

            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise


    # ==================== DELETE ====================

    def delete(self, user_id: int) -> bool:
        """
        사용자 삭제

        Args:
        - user_id (int): 사용자 ID

        Returns:
        - bool: 삭제 성공 여부

        Note:
        - CASCADE DELETE: 사용자의 게시글, 댓글도 자동 삭제 (ORM 설정)
        """
        user = self.find_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True
