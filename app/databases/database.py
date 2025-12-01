"""
Database Configuration

역할:
1. SQLAlchemy Engine 및 Session 설정
2. 데이터베이스 연결 관리
3. Base 클래스 정의 (ORM 모델들의 부모 클래스)

사용 데이터베이스:
- SQLite (무료, 파일 기반, 설치 불필요)
- 개발/테스트에 적합
- 프로덕션: PostgreSQL, MySQL 등으로 전환 가능

설계 원칙:
- Dependency Injection: get_db()를 통한 세션 주입
- Context Manager: 자동 세션 관리 (commit/rollback)

정의:
- DATABASE_URL: 데이터베이스 연결 문자열
- engine: SQLAlchemy Engine 객체
- SessionLocal: 데이터베이스 세션 생성기
- Base: ORM 모델들의 부모 클래스
- get_db(): 데이터베이스 세션 의존성 주입 함수
- init_db(): 데이터베이스 초기화 함수
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator


# ==================== 몰랐던 용어 정리 ====================

# ORM (Object-Relational Mapping): OOP 언어의 객체와 관계형 데이터베이스의 테이블 간의 변환을 자동화하는 기술
# Transaction 트랜잭션: 여러 개의 데이터베이스 작업을 하나의 묶음으로 처리하는 것 (여러 작업이 모두 성공하거나 모두 실패)
#   * Commit - 트랜잭션의 모든 작업을 실제로 저장
#   * Rollback - 트랜잭션의 모든 작업을 취소하고 원상복구
#   * pros1: 원자성(Atomicity): 모두 성공 또는 모두 실패
#   * pros2: 일관성(Consistency): 데이터 무결성 유지
# Flush: 메모리의 변경사항을 SQL로 변환해서 데이터베이스에 전송

# ==================== Database Configuration ====================

# SQLite 데이터베이스 파일 경로
# 상대 경로: 프로젝트 루트에 community.db 파일 생성
DATABASE_URL = "sqlite:///./community.db"

# SQLAlchemy Engine 생성
# check_same_thread=False: SQLite는 기본적으로 단일 스레드만 허용
#                          FastAPI는 멀티스레드 환경이므로 해제 필요
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # SQL 쿼리 로깅 (개발 시 유용, 프로덕션에서는 False)
)

# Session Local: 데이터베이스 세션 생성기
# Session: 데이터베이스와 거래(조회, 추가, 수정, 삭제)를 할 수 있는 통로
SessionLocal = sessionmaker(
    autocommit=False, # 명시적 commit 필요 (변경사항을 자동으로 저장하지 않음 / 데이터 일관성 유지)
    autoflush=False,  # 명시적 flush 필요 (자동으로 데이터베이스에 변경사항을 반영하지 않음 / 성능 최적화)
    bind=engine       # 위에서 만든 engine과 연결
)

# Base: ORM (데이터베이스 테이블) 모델들의 부모 클래스
# 모든 ORM 모델은 이 Base를 상속받음
Base = declarative_base()


# ==================== Dependency Injection ====================

def get_db() -> Generator:
    """
    데이터베이스 세션 의존성 주입 함수

    FastAPI의 Depends()와 함께 사용
    각 요청마다 새로운 세션을 생성하고, 요청 완료 후 자동으로 닫음

    Yields:
    - db: SQLAlchemy Session 객체

    사용 예시:
    ```python
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    ```

    트랜잭션 관리:
    - 성공 시: 자동 commit
    - 실패 시: 자동 rollback
    - 항상: 세션 close
    """
    db = SessionLocal() # 새로운 세션 생성
    try:
        yield db        # 세션을 전달자(FastAPI)에 전달
    #    db.commit()    # 트랜잭션 커밋
    #except Exception:
    #    db.rollback()  # 오류 발생 시 롤백
    finally:
        db.close()      # 세션 닫기


# ==================== Database Initialization ====================

def init_db():
    """
    데이터베이스 초기화 함수

    모든 ORM 모델의 테이블을 생성
    - 이미 테이블이 존재하면 스킵
    - 개발 환경에서만 사용 (프로덕션은 Alembic 마이그레이션 사용)

    호출 시점:
    - 서버 시작 시 (main.py의 lifespan 이벤트)
    """
    from app.databases.db_models import User, Post, Comment  # 순환 import 방지
    Base.metadata.create_all(bind=engine)
    # 모든 테이블을 데이터베이스에 생성
    # 이미 테이블이 있으면 건너뜀 (안전)
    print("Database initialized.")