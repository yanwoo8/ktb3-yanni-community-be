"""
Auth Routes (Database Version)

역할:
1. 회원 정보 / 인증 관련 HTTP 요청/응답 처리: Request → Controller → Response
2. 상태 코드 매핑: Controller 예외 → HTTP Status Code
3. 경로 라우팅: URL 패턴 정의 (엔드포인트 설계)
4. 데이터베이스 세션 관리: Dependency Injection

설계 원칙: RESTful API
- 얇은 계층(Thin Layer): 비즈니스 로직은 Controller에 위임
- 단일 책임 원칙(SRP): HTTP 계층만 담당
- 의존성 주입: DB Session → Model → Controller

Endpoints:
- POST /auth/register: 회원가입
- GET /auth/check-email/{email}: 이메일 중복 확인
- GET /auth/check-nickname/{nickname}: 닉네임 중복 확인
- POST /auth/login: 로그인
- PATCH /auth/users/{user_id}/nickname: 닉네임 수정
- DELETE /auth/users/{user_id}: 회원 탈퇴
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database import get_db
from app.models.user_model import UserModel
from app.controllers.user_controller import UserController
from app.schemas.auth_schema import UserRegister, UserLogin, NicknameUpdate
import logging


# ==================== Router Setup ====================

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Logger 설정
logger = logging.getLogger(__name__)


# ==================== Helper Functions ====================

def get_user_controller(db: Session = Depends(get_db)) -> UserController:
    """
    UserController 의존성 주입 함수

    Args:
    - db (Session): 데이터베이스 세션

    Returns:
    - UserController: 사용자 컨트롤러 인스턴스
    """
    user_model = UserModel(db)
    return UserController(user_model)


# ==================== API Endpoints ====================

@router.post("/register", status_code=201)
def register(
    user_data: UserRegister,
    controller: UserController = Depends(get_user_controller)
) -> Dict:
    """
    회원가입 API (POST /auth/register)

    Args:
    - user_data (UserRegister): 회원가입 요청 데이터
    - controller (UserController): 의존성 주입된 컨트롤러

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

    except IntegrityError as e:
        logger.error(f"회원가입 실패 (DB 제약 위반) - email: {user_data.email}, error: {str(e)}")
        raise HTTPException(status_code=400, detail="이메일 또는 닉네임이 이미 사용 중입니다")

    except SQLAlchemyError as e:
        logger.error(f"회원가입 실패 (DB 오류) - email: {user_data.email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"회원가입 실패 - email: {user_data.email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다")


@router.get("/check-email/{email}")
def check_email_duplicate(
    email: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    이메일 중복 확인 API (GET /auth/check-email/{email})

    Args:
    - email (str): 확인할 이메일
    - db (Session): 데이터베이스 세션

    Returns:
    - Dict: 중복 여부 정보

    Status Code:
    - 200 OK: 확인 성공
    - 500 Internal Server Error: 서버 오류
    """
    try:
        user_model = UserModel(db)
        existing_user = user_model.find_by_email(email)
        is_duplicate = existing_user is not None

        return {
            "email": email,
            "is_duplicate": is_duplicate,
            "message": "*중복된 이메일입니다" if is_duplicate else "사용 가능한 이메일입니다"
        }

    except SQLAlchemyError as e:
        logger.error(f"이메일 중복 확인 실패 (DB 오류) - email: {email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"이메일 중복 확인 실패 - email: {email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="이메일 확인 중 오류가 발생했습니다")


@router.get("/check-nickname/{nickname}")
def check_nickname_duplicate(
    nickname: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    닉네임 중복 확인 API (GET /auth/check-nickname/{nickname})

    Args:
    - nickname (str): 확인할 닉네임
    - db (Session): 데이터베이스 세션

    Returns:
    - Dict: 중복 여부 정보

    Status Code:
    - 200 OK: 확인 성공
    - 500 Internal Server Error: 서버 오류
    """
    try:
        user_model = UserModel(db)
        existing_user = user_model.find_by_nickname(nickname)
        is_duplicate = existing_user is not None

        return {
            "nickname": nickname,
            "is_duplicate": is_duplicate,
            "message": "*중복된 닉네임 입니다." if is_duplicate else "사용 가능한 닉네임입니다"
        }

    except SQLAlchemyError as e:
        logger.error(f"닉네임 중복 확인 실패 (DB 오류) - nickname: {nickname}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"닉네임 중복 확인 실패 - nickname: {nickname}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="닉네임 확인 중 오류가 발생했습니다")


@router.post("/login", status_code=200)
def login(
    login_data: UserLogin,
    controller: UserController = Depends(get_user_controller)
) -> Dict:
    """
    로그인 API (POST /auth/login)

    Args:
    - login_data (UserLogin): 로그인 요청 데이터
    - controller (UserController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 로그인 성공 메시지 + 사용자 정보

    Status Code:
    - 200 OK: 로그인 성공
    - 400 Bad Request: 로그인 실패
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

    except SQLAlchemyError as e:
        logger.error(f"로그인 실패 (DB 오류) - email: {login_data.email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"로그인 실패 - email: {login_data.email}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다")


# ==================== UPDATE ====================

@router.patch("/users/{user_id}/nickname")
def update_user_nickname(
    user_id: int,
    update_data: NicknameUpdate,
    controller: UserController = Depends(get_user_controller)
) -> Dict:
    """
    닉네임 수정 API (PATCH /auth/users/{user_id}/nickname)

    Args:
    - user_id (int): 사용자 ID
    - update_data (NicknameUpdate): 새 닉네임
    - controller (UserController): 의존성 주입된 컨트롤러

    Returns:
    - Dict: 수정 성공 메시지 + 사용자 정보

    Status Code:
    - 200 OK: 수정 성공
    - 400 Bad Request: 닉네임 중복 또는 사용자 없음
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

    except IntegrityError as e:
        logger.error(f"닉네임 수정 실패 (DB 제약 위반) - user_id: {user_id}, error: {str(e)}")
        raise HTTPException(status_code=400, detail="닉네임이 이미 사용 중입니다")

    except SQLAlchemyError as e:
        logger.error(f"닉네임 수정 실패 (DB 오류) - user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"닉네임 수정 실패 - user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="닉네임 수정 중 오류가 발생했습니다")


# ==================== DELETE ====================

@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    controller: UserController = Depends(get_user_controller)
):
    """
    회원 탈퇴 API (DELETE /auth/users/{user_id})

    Args:
    - user_id (int): 사용자 ID
    - controller (UserController): 의존성 주입된 컨트롤러

    Returns:
    - None (204 No Content)

    Status Code:
    - 204 No Content: 회원 탈퇴 성공
    - 400 Bad Request: 사용자가 존재하지 않음
    - 500 Internal Server Error: 서버 오류

    Note:
    - CASCADE DELETE: 게시글, 댓글도 자동 삭제 (데이터베이스 제약)
    """
    try:
        controller.delete_user(user_id=user_id)
        return None

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        logger.error(f"회원 탈퇴 실패 (DB 오류) - user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다")

    except Exception as e:
        logger.error(f"회원 탈퇴 실패 - user_id: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="회원 탈퇴 중 오류가 발생했습니다")
