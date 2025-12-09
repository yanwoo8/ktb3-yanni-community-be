"""
Auth Pydantic Schemas

Pydantic BaseModel의 역할:
1. 데이터 검증 (Validation): 타입 체크, 필수 필드 확인, 커스텀 검증
2. 직렬화 (Serialization): JSON ↔ Python Object 변환
3. API 문서화: OpenAPI 스펙에 자동 등록

설계 원칙:
- 단일 책임 원칙(SRP): 데이터 검증만 담당
- 불변성: 입력 데이터의 형식만 정의, 비즈니스 로직은 Controller에서 처리

==============================
1. UserRegister: 회원가입 요청 바디 스키마 (POST /auth/register)
- validate_email
- validate_password
- validate_nickname
==============================
2. UserLogin: 로그인 요청 바디 스키마 (POST /auth/login)
- validate_email
- validate_password
==============================
3. NicknameUpdate: 닉네임 수정 요청 스키마 (PATCH /auth/users/{user_id}/nickname)
- validate_nickname
==============================
4. UserResponse: 사용자 정보 응답 스키마
- 타입 정의만 포함, 비밀번호 제외
- 현재 사용 X 현재는 Dict로 응답 처리
==============================
"""

import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field, ValidationError



class UserRegister(BaseModel):
    """
    @ Pydantic Model
    [POST] 회원가입 요청 바디 스키마
    auth_route.py > register 함수

    Fields:
    - email (str): 이메일 (필수, 이메일 형식)
    - password (str): 비밀번호 (필수, 8-20자, 대소문자+숫자+특수문자)
    - password_confirm (str): 비밀번호 확인 (필수)
    - nickname (str): 닉네임 (필수, 띄어쓰기 불가, 10자 이내)
    - profile_image (Optional[str]): 프로필 이미지 URL/경로 (선택)

    Note:
    - EmailStr: pydantic의 이메일 검증 타입
    - field_validator: 커스텀 검증 로직
    """

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=20)
    password_confirm: str = Field(..., min_length=1)
    nickname: str = Field(..., min_length=1, max_length=10)
    profile_image: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """이메일 형식 검증"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*이메일을 입력해주세요.")
        
        if len(v) < 5:  # 최소 a@b.c 형식
            raise ValueError("*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)")
        
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """
        비밀번호 유효성 검증:
        - 8자 이상, 20자 이하
        - 대문자, 소문자, 숫자, 특수문자 각각 최소 1개 포함
        """
        pwmessage = "*비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."

        if not v or len(v.strip()) == 0:
            raise ValueError("*비밀번호를 입력해주세요")

        if len(v) < 8 or len(v) > 20:
            raise ValueError(pwmessage)

        # 대문자, 소문자, 숫자, 특수문자 포함 여부 확인
        has_upper = bool(re.search(r'[A-Z]', v))
        has_lower = bool(re.search(r'[a-z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(pwmessage)

        return v

    @field_validator('password_confirm')
    @classmethod
    def validate_password_confirm(cls, v, info):
        """
        비밀번호 확인 검증:
        1. 빈 값이 아닌지 확인
        2. password와 일치하는지 확인
        """
        # 1. 빈 값 검증
        if not v or len(v.strip()) == 0:
            raise ValueError("*비밀번호 확인을 입력해주세요")

        # 2. 비밀번호 일치 검증
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("*비밀번호가 일치하지 않습니다.")

        return v

    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v):
        """
        닉네임 유효성 검증:
        - 띄어쓰기 불가
        - 10글자 이내
        """
        if not v or len(v.strip()) == 0:
            raise ValueError("*닉네임을 입력해주세요")

        if ' ' in v:
            raise ValueError("*띄어쓰기를 없애주세요")

        if len(v) > 10:
            raise ValueError("*닉네임은 최대 10자 까지 작성 가능합니다.")

        return v


class UserLogin(BaseModel):
    """
    @ Pydantic Model
    [POST] 로그인 요청 바디 스키마
    auth_route.py > login 함수

    Fields:
    - email (str): 이메일 (필수)
    - password (str): 비밀번호 (필수)

    Note:
    - 로그인은 기본적인 필드 검증만 수행
    - 실제 인증은 Controller에서 처리
    """
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """이메일 형식 검증"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)")
        if len(v) < 5:
            raise ValueError("*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)")
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """비밀번호 입력 확인"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*비밀번호를 입력해주세요")
        return v



class NicknameUpdate(BaseModel):
    """
    @ Pydantic Model
    [PATCH] 닉네임 수정 요청 스키마
    auth_routes.py > update_user_nickname 함수

    Fields:
    - nickname (str): 새 닉네임 (필수, 띄어쓰기 불가, 10자 이내)

    Note:
    - UserRegister의 닉네임 검증과 동일한 로직
    """
    nickname: str = Field(..., min_length=1, max_length=10)

    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v):
        """
        닉네임 유효성 검증:
        - 띄어쓰기 불가
        - 10글자 이내
        """
        if not v or len(v.strip()) == 0:
            raise ValueError("*닉네임을 입력해주세요")

        if ' ' in v:
            raise ValueError("*띄어쓰기를 없애주세요")

        if len(v) > 10:
            raise ValueError("*닉네임은 최대 10자 까지 작성 가능합니다.")

        return v



class UserResponse(BaseModel):
    """
    @ Pydantic Model
    사용자 정보 응답 스키마
    현재 사용 X, Dict로 응답 처리

    Fields:
    - id (int): 사용자 ID
    - email (str): 이메일
    - nickname (str): 닉네임
    - profile_image (Optional[str]): 프로필 이미지

    Note:
    - 비밀번호는 응답에 포함하지 않음 (보안)
    """
    id: int
    email: str
    nickname: str
    profile_image: Optional[str] = None
