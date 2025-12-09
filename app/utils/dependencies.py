"""
Authentication Dependencies

역할:
1. HTTP 요청에서 JWT 토큰 추출
2. 토큰 검증 및 사용자 정보 조회
3. FastAPI Depends()와 함께 사용하여 인증 필요한 엔드포인트 보호

설계 원칙:
- 의존성 주입 패턴: FastAPI의 Depends() 메커니즘 활용
- 재사용성: 여러 라우터에서 공통으로 사용

Usage:
```python
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
```
"""

from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.utils.auth import verify_token
from app.databases import get_db
from app.models.user_model import UserModel


# ==================== HTTP Bearer Token Scheme ====================

# HTTPBearer: Authorization 헤더에서 Bearer 토큰 추출
# auto_error=False: 토큰이 없어도 에러를 자동으로 발생시키지 않음 (커스텀 에러 메시지 사용)
security = HTTPBearer(auto_error=False)


# ==================== Authentication Dependency ====================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Dict:
    """
    현재 로그인한 사용자 정보 반환

    Authorization 헤더에서 JWT 토큰을 추출하고 검증하여
    로그인한 사용자의 정보를 반환합니다.

    Args:
    - credentials (HTTPAuthorizationCredentials): Bearer 토큰
    - db (Session): 데이터베이스 세션

    Returns:
    - Dict: 사용자 정보 (id, email, nickname, profile_image)

    Raises:
    - HTTPException 401: 토큰이 없거나 유효하지 않은 경우
    - HTTPException 404: 사용자를 찾을 수 없는 경우

    Usage:
    ```python
    @router.post("/posts")
    def create_post(
        current_user: dict = Depends(get_current_user)
    ):
        author_id = current_user["id"]
        # ...
    ```

    HTTP Request Example:
    ```
    POST /posts
    Headers:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    # 1. 토큰 존재 확인
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다. 로그인 후 다시 시도해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 2. 토큰 검증
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다. 다시 로그인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 사용자 ID 추출
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다. 다시 로그인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. 데이터베이스에서 사용자 조회
    user_model = UserModel(db)
    user = user_model.find_by_id(int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    # 5. 사용자 정보 반환 (비밀번호 제외)
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "profile_image": user.profile_image
    }


# ==================== Optional Authentication Dependency ====================

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Dict]:
    """
    선택적 인증: 로그인하지 않아도 접근 가능하지만, 로그인한 경우 사용자 정보 반환

    토큰이 없어도 에러를 발생시키지 않고 None을 반환합니다.
    로그인 여부에 따라 다른 동작을 하는 엔드포인트에 사용합니다.

    Args:
    - credentials (HTTPAuthorizationCredentials): Bearer 토큰 (선택)
    - db (Session): 데이터베이스 세션

    Returns:
    - Optional[Dict]: 로그인한 경우 사용자 정보, 아니면 None

    Usage:
    ```python
    @router.get("/posts")
    def get_posts(
        current_user: Optional[dict] = Depends(get_current_user_optional)
    ):
        if current_user:
            # 로그인한 사용자: 추천 게시글 제공
            pass
        else:
            # 비로그인 사용자: 기본 게시글 제공
            pass
    ```
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
