"""
User Model

역할:
1. 데이터 접근 계층 (Data Access Layer): In-memory 저장소 관리
2. CRUD 연산: 사용자 데이터 생성, 조회, 수정, 삭제
3. 데이터 무결성: 중복 검증, 존재 여부 확인

설계 원칙:
- 단일 책임 원칙(SRP): 데이터 접근만 담당
- 비즈니스 로직 분리: Controller에서 처리
- Repository 패턴: 데이터 소스 추상화

Note:
- 현재는 In-memory 저장소 (List[Dict])
- 실제 프로덕션에서는 DB ORM (SQLAlchemy 등) 사용
"""

from typing import List, Dict, Optional


class UserModel:
    """
    사용자 데이터 접근 계층

    Attributes:
    - users (List[Dict]): In-memory 사용자 저장소

    Methods:
    - create: 사용자 생성
    - find_by_id: ID로 사용자 조회
    - find_by_email: 이메일로 사용자 조회
    - find_by_nickname: 닉네임으로 사용자 조회
    - find_all: 전체 사용자 조회
    - update: 사용자 정보 수정
    - delete: 사용자 삭제
    """

    def __init__(self):
        """Model 초기화"""
        self.users: List[Dict] = []
        self._next_id: int = 1  # 다음 사용자 ID를 추적하는 카운터


    # ==================== CREATE ====================

    def create(self, email: str, password: str, nickname: str,
               profile_image: Optional[str] = None) -> Dict:
        """
        사용자 생성

        Args:
        - email (str): 이메일
        - password (str): 비밀번호 (해시화된 값)
        - nickname (str): 닉네임
        - profile_image (Optional[str]): 프로필 이미지 URL

        Returns:
        - Dict: 생성된 사용자 정보 (비밀번호 제외)

        Note:
        - ID는 삭제 후에도 중복되지 않도록 _next_id 카운터 사용
        """
        new_user = {
            "id": self._next_id,
            "email": email,
            "password": password,
            "nickname": nickname,
            "profile_image": profile_image
        }
        self.users.append(new_user)
        self._next_id += 1  # 다음 ID를 위해 증가

        # 비밀번호를 제외한 정보 반환
        return {
            "id": new_user["id"],
            "email": new_user["email"],
            "nickname": new_user["nickname"],
            "profile_image": new_user["profile_image"]
        }


    # ==================== READ ====================

    def find_by_id(self, user_id: int) -> Optional[Dict]:
        """
        ID로 사용자 조회

        Args:
        - user_id (int): 사용자 ID

        Returns:
        - Optional[Dict]: 사용자 정보 (없으면 None)
        """
        return next((u for u in self.users if u["id"] == user_id), None)


    def find_by_email(self, email: str) -> Optional[Dict]:
        """
        이메일로 사용자 조회

        Args:
        - email (str): 이메일

        Returns:
        - Optional[Dict]: 사용자 정보 (없으면 None)
        """
        return next((u for u in self.users if u["email"] == email), None)


    def find_by_nickname(self, nickname: str) -> Optional[Dict]:
        """
        닉네임으로 사용자 조회

        Args:
        - nickname (str): 닉네임

        Returns:
        - Optional[Dict]: 사용자 정보 (없으면 None)
        """
        return next((u for u in self.users if u["nickname"] == nickname), None)


    def find_all(self) -> List[Dict]:
        """
        전체 사용자 조회

        Returns:
        - List[Dict]: 전체 사용자 목록 (비밀번호 제외)
        """
        return [
            {
                "id": u["id"],
                "email": u["email"],
                "nickname": u["nickname"],
                "profile_image": u["profile_image"]
            }
            for u in self.users
        ]


    # ==================== UPDATE ====================

    def update(self, user_id: int, **kwargs) -> Optional[Dict]:
        """
        사용자 정보 수정

        Args:
        - user_id (int): 사용자 ID
        - **kwargs: 수정할 필드들 (nickname, profile_image 등)

        Returns:
        - Optional[Dict]: 수정된 사용자 정보 (없으면 None)
        """
        for i, user in enumerate(self.users):
            if user["id"] == user_id:
                # 전달된 필드만 업데이트
                for key, value in kwargs.items():
                    if key in user and value is not None:
                        self.users[i][key] = value

                # 비밀번호 제외하고 반환
                return {
                    "id": self.users[i]["id"],
                    "email": self.users[i]["email"],
                    "nickname": self.users[i]["nickname"],
                    "profile_image": self.users[i]["profile_image"]
                }

        return None


    # ==================== DELETE ====================

    def delete(self, user_id: int) -> bool:
        """
        사용자 삭제

        Args:
        - user_id (int): 사용자 ID

        Returns:
        - bool: 삭제 성공 여부
        """
        for i, user in enumerate(self.users):
            if user["id"] == user_id:
                self.users.pop(i)
                return True

        return False
