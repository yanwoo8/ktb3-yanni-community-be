"""
Comment Pydantic Schemas

Pydantic BaseModel의 역할:
1. 데이터 검증 (Validation): 타입 체크, 필수 필드 확인
2. 직렬화 (Serialization): JSON ↔ Python Object 변환
3. API 문서화: OpenAPI 스펙에 자동 등록

설계 원칙:
- 단일 책임 원칙(SRP): 데이터 검증만 담당
- 불변성: 입력 데이터의 형식만 정의, 비즈니스 로직은 Controller에서 처리
"""

from typing import Optional
from pydantic import BaseModel, field_validator


class CommentCreate(BaseModel):
    """
    @ Pydantic Model
    [POST] 댓글 생성 요청 바디 스키마

    Fields:
    - post_id (int): 게시글 ID (필수)
    - content (str): 댓글 내용 (필수)

    Note:
    - author_id는 JWT 토큰에서 자동으로 추출되므로 제외
    - FastAPI는 이 모델을 보고 자동으로 request body 파싱
    - 타입 불일치 시 422 Unprocessable Entity 반환
    """
    post_id: int
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """댓글 내용 유효성 검증"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*댓글 내용을 입력해주세요")
        return v


class CommentUpdate(BaseModel):
    """
    @ Pydantic Model
    [PUT/PATCH] 댓글 수정 요청 바디 스키마

    Fields:
    - content (str): 댓글 내용 (필수)

    Note:
    - 댓글 수정은 내용만 수정 가능
    """
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """댓글 내용 유효성 검증"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*댓글 내용을 입력해주세요")
        return v


class CommentResponse(BaseModel):
    """
    댓글 응답 스키마

    Fields:
    - id (int): 댓글 ID
    - post_id (int): 게시글 ID
    - author_id (int): 작성자 ID
    - author_nickname (str): 작성자 닉네임
    - author_profile_image (Optional[str]): 작성자 프로필 이미지
    - content (str): 댓글 내용
    - created_at (str): 작성일시 (yyyy-mm-dd hh:mm:ss)
    """
    id: int
    post_id: int
    author_id: int
    author_nickname: str
    author_profile_image: Optional[str] = None
    content: str
    created_at: str
