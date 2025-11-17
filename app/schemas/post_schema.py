"""
Post Pydantic Schemas

Pydantic BaseModel의 역할:
1. 데이터 검증 (Validation): 타입 체크, 필수 필드 확인
2. 직렬화 (Serialization): JSON ↔ Python Object 변환
3. API 문서화: OpenAPI 스펙에 자동 등록

설계 원칙:
- 단일 책임 원칙(SRP): 데이터 검증만 담당
- 불변성: 입력 데이터의 형식만 정의, 비즈니스 로직은 Controller에서 처리
"""



from typing import Optional
from pydantic import BaseModel, Field, field_validator




class PostCreate(BaseModel):
    """
    @ Pydantic Model
    [POST/PUT] 게시글 생성/전체수정 요청 바디 스키마

    Fields:
    - title (str): 게시글 제목 (필수, 최대 26자)
    - content (str): 게시글 내용 (필수)
    - image_url (Optional[str]): 이미지 URL (선택)
    - author_id (int): 작성자 ID (필수)

    Note:
    - FastAPI는 이 모델을 보고 자동으로 request body 파싱
    - 타입 불일치 시 422 Unprocessable Entity 반환
    """
    title: str = Field(..., max_length=26)
    content: str
    image_url: Optional[str] = None
    author_id: int

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """제목 검증"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*제목을 입력해주세요")
        if len(v) > 26:
            raise ValueError("*제목은 최대 26자까지 작성 가능합니다.")
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """내용 검증"""
        if not v or len(v.strip()) == 0:
            raise ValueError("*내용을 입력해주세요")
        return v


class PostPartialUpdate(BaseModel):
    """
    [PATCH] 게시글 부분 수정 요청 스키마
    [PATCH] Post Update(partial) Request Body Schema
    
    Fields:
    - title (Optional[str]): 게시글 제목 (선택)
    - content (Optional[str]): 게시글 내용 (선택)
    
    Note:
    - Optional[str] = None으로 클라이언트가 선택적으로 필드 전송
    - exclude_unset=True와 함께 사용하여 전송된 필드만 추출 & 업데이트
    """
    title: Optional[str] = None
    content: Optional[str] = None



