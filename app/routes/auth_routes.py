"""
Auth Routes

역할:
1. 회원 정보 / 인증 관련 HTTP 요청/응답 처리: Request → Controller → Response
2. 상태 코드 매핑: Controller 예외 → HTTP Status Code
3. 경로 라우팅: URL 패턴 정의 (엔드포인트 설계)

설계 원칙: RESTful API
- 얇은 계층(Thin Layer): 비즈니스 로직은 Controller에 위임
- 단일 책임 원칙(SRP): HTTP 계층만 담당
- 의존성 주입: Controller 인스턴스를 주입받아 사용

Note:
- APIRouter: FastAPI의 모듈화된 라우팅 시스템
- HTTPException: FastAPI의 HTTP 예외 클래스

외부 클래스들:
- UserRegister: 회원가입 요청 바디 스키마
- UserLogin: 로그인 요청 바디 스키마
--------------------------------------
- UserController: 사용자 관련 비즈니스 로직 처리
- PostController: 게시글 관련 비즈니스 로직 처리
- CommentController: 댓글 관련 비즈니스 로직 처리

Endpoints:
- POST /auth/register: 회원가입
- POST /auth/login: 로그인
- PATCH /auth/users/{user_id}/nickname: 닉네임 수정
- DELETE /auth/users/{user_id}: 회원 탈퇴
"""

from typing import Dict
from fastapi import APIRouter, HTTPException
from app.schemas.auth_schema import UserRegister, UserLogin, NicknameUpdate
from app.controllers.controller_instances import user_controller, post_controller, comment_controller
import logging


# ==================== Router Setup ====================

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Controller 인스턴스 (공유 Singleton)
controller = user_controller

# Logger 인스턴스 생성
logger = logging.getLogger(__name__)


# ==================== API Endpoints ====================

@router.post("/register", status_code=201)
def register(user_data: UserRegister) -> Dict:
    """
    회원가입 API (POST /auth/register)

    Args:
    - user_data (UserRegister): 회원가입 요청 데이터

    Returns:
    - Dict: 회원가입 성공 메시지 + 사용자 정보

    Status Code:
    - 201 Created: 회원가입 성공
    - 400 Bad Request: 유효성 검증 실패
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.register(
            email=user_data.email,
            password=user_data.password,
            password_confirm=user_data.password_confirm,
            nickname=user_data.nickname,
            profile_image=user_data.profile_image
        )
        return {"message": "회원가입 성공", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"회원가입 실패 - email: {user_data.email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다")


@router.post("/login", status_code=200)
def login(login_data: UserLogin) -> Dict:
    """
    로그인 API (POST /auth/login)

    Args:
    - email (str): 이메일
    - password (str): 비밀번호

    Returns:
    - Dict: 로그인 성공 메시지 + 사용자 정보

    Status Code:
    - 200 OK: 로그인 성공
    - 400 Bad Request: 유효성 검증 실패 또는 로그인 실패
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.login(
            email=login_data.email,
            password=login_data.password
        )
        return {"message": "로그인 성공", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"로그인 실패 - email: {login_data.email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다")


# ==================== UPDATE ====================

@router.patch("/users/{user_id}/nickname")
def update_user_nickname(user_id: int, update_data: NicknameUpdate) -> Dict:
    """
    닉네임 수정 API (PATCH /auth/users/{user_id}/nickname)

    Args:
    - user_id (int): 사용자 ID
    - update_data (NicknameUpdate): 새 닉네임

    Returns:
    - Dict: 수정 성공 메시지 + 사용자 정보

    Status Code:
    - 200 OK: 수정 성공
    - 400 Bad Request: 유효성 검증 실패 또는 닉네임 중복
    - 500 Internal Server Error: 서버 오류
    """
    try:
        result = controller.update_nickname(
            user_id=user_id,
            new_nickname=update_data.nickname
        )
        return {"message": "수정완료", "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"닉네임 수정 실패 - user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="닉네임 수정 중 오류가 발생했습니다")


# ==================== DELETE ====================

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """
    회원 탈퇴 API (DELETE /auth/users/{user_id})

    Args:
    - user_id (int): 사용자 ID

    Returns:
    - None (204 No Content)

    Status Code:
    - 204 No Content: 회원 탈퇴 성공
    - 400 Bad Request: 사용자가 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - 회원 탈퇴 시 작성한 게시글과 댓글이 모두 삭제됨
    """
    try:
        controller.delete_user(
            user_id=user_id,
            post_controller=post_controller,
            comment_controller=comment_controller
        )
        return None

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"회원 탈퇴 실패 - user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="회원 탈퇴 중 오류가 발생했습니다")
