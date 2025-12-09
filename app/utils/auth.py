"""
JWT Authentication Utilities

역할:
1. JWT 토큰 생성 (create_access_token)
2. JWT 토큰 검증 및 디코딩 (verify_token)
3. 비밀번호 해싱 및 검증 (hash_password, verify_password)

설계 원칙:
- 단일 책임 원칙(SRP): 인증 관련 유틸리티만 담당
- 재사용성: 여러 모듈에서 사용 가능한 독립적인 함수

Dependencies:
- python-jose: JWT 토큰 생성 및 검증
- passlib: 비밀번호 해싱 (bcrypt 알고리즘)
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError
from jose import jwt
from passlib.context import CryptContext


# ==================== Configuration ====================

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== Password Hashing ====================

def hash_password(password: str) -> str:
    """
    비밀번호를 bcrypt 알고리즘으로 해싱

    Args:
    - password (str): 평문 비밀번호

    Returns:
    - str: 해싱된 비밀번호

    Example:
    >>> hash_password("MyPassword123!")
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교

    Args:
    - plain_password (str): 평문 비밀번호
    - hashed_password (str): 해싱된 비밀번호

    Returns:
    - bool: 일치 여부

    Example:
    >>> hashed = hash_password("MyPassword123!")
    >>> verify_password("MyPassword123!", hashed)
    True
    >>> verify_password("WrongPassword", hashed)
    False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT Token ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token 생성

    Args:
    - data (dict): 토큰에 포함할 데이터 (예: {"sub": "user_id"})
    - expires_delta (Optional[timedelta]): 토큰 만료 시간 (기본값: 7일)

    Returns:
    - str: JWT 토큰 문자열

    Token Payload 구조:
    {
        "sub": "1",  # subject (사용자 ID)
        "exp": 1234567890  # expiration time (만료 시간)
    }

    Example:
    >>> token = create_access_token(data={"sub": "1"})
    >>> print(token)
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    JWT 토큰 검증 및 디코딩

    Args:
    - token (str): JWT 토큰 문자열

    Returns:
    - Optional[Dict]: 토큰이 유효하면 페이로드 반환, 그렇지 않으면 None

    Example:
    >>> token = create_access_token(data={"sub": "1"})
    >>> payload = verify_token(token)
    >>> print(payload)
    {'sub': '1', 'exp': 1234567890}

    >>> verify_token("invalid-token")
    None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
