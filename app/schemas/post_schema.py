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
from pydantic import BaseModel




class PostCreate(BaseModel):
    """
    @ Pydantic Model
    [POST/PUT] 게시글 생성/전체수정 요청 바디 스키마
    [POST/PUT] Post Create/Update(full) Request Body Schema
    
    Fields:
    - title (str): 게시글 제목 (필수)
    - content (str): 게시글 내용 (필수)
    
    Note:
    - FastAPI는 이 모델을 보고 자동으로 request body 파싱
    - 타입 불일치 시 422 Unprocessable Entity 반환
    """
    title: str
    content: str


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



