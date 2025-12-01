"""
User Controller

역할:
1. 비즈니스 로직 처리: 회원가입, 로그인 등 사용자 인증 로직
2. Model 계층 호출: 데이터 접근은 UserModel에 위임
3. 예외 처리: 비즈니스 규칙 위반 시 예외 발생

설계 원칙:
- 단일 책임 원칙(SRP): 사용자 인증 관련 비즈니스 로직만 담당
- 의존성 역전 원칙(DIP): HTTP 계층 및 데이터 계층과 독립적
- Repository 패턴: Model을 통한 데이터 접근

Note:
- Controller → Model → Data 계층 분리
- 비밀번호는 실제로는 해싱하여 저장해야 함 (bcrypt, argon2 등)
"""

from typing import Dict, Optional
from app.models.user_model import UserModel


class UserController:
    """
    사용자 인증 비즈니스 로직을 담당하는 Controller

    Attributes:
    - user_model (UserModel): 사용자 데이터 접근 계층

    Methods:
    - register: 회원가입
    - login: 로그인
    - get_user_info: 사용자 정보 조회 (내부용)
    - update_nickname: 닉네임 수정
    - delete_user: 회원 탈퇴
    """

    def __init__(self, user_model: UserModel):
        """
        Controller 초기화

        Args:
        - user_model (UserModel): 의존성 주입된 UserModel 인스턴스
        """
        self.user_model = user_model


    # ==================== REGISTER ====================

    def register(self, email: str, password: str, password_confirm: str,
                 nickname: str, profile_image: Optional[str] = None) -> Dict:
        """
        회원가입

        Args:
        - email (str): 이메일
        - password (str): 비밀번호
        - password_confirm (str): 비밀번호 확인
        - nickname (str): 닉네임
        - profile_image (Optional[str]): 프로필 이미지

        Returns:
        - Dict: 생성된 사용자 정보 (비밀번호 제외)

        Raises:
        - ValueError: 유효성 검증 실패 시

        Business Logic:
        1. 프로필 사진 확인
        2. 이메일 중복 확인
        3. 비밀번호 확인 일치 여부
        4. 닉네임 중복 확인
        5. 사용자 생성 및 저장
        """

        # 1. 프로필 사진 확인
        if not profile_image:
            raise ValueError("*프로필 사진을 추가해주세요")

        # 2. 이메일 중복 확인
        if self.user_model.find_by_email(email):
            raise ValueError("*중복된 이메일입니다")

        # 3. 비밀번호 확인 일치 여부
        if password != password_confirm:
            raise ValueError("*비밀번호가 다릅니다")

        # 4. 닉네임 중복 확인
        if self.user_model.find_by_nickname(nickname):
            raise ValueError("*중복된 닉네임 입니다.")

        # 5. 사용자 생성 (Model에 위임)
        created_user = self.user_model.create(
            email=email,
            password=password,  # 실제로는 해싱하여 저장해야 함
            nickname=nickname,
            profile_image=profile_image
        )

        # ORM 객체를 Dict로 변환하여 반환
        return {
            "id": created_user.id,
            "email": created_user.email,
            "nickname": created_user.nickname,
            "profile_image": created_user.profile_image
        }


    # ==================== LOGIN ====================

    def login(self, email: str, password: str) -> Dict:
        """
        로그인

        Args:
        - email (str): 이메일
        - password (str): 비밀번호

        Returns:
        - Dict: 로그인한 사용자 정보 (비밀번호 제외)

        Raises:
        - ValueError: 로그인 실패 시

        Business Logic:
        1. 이메일로 사용자 찾기
        2. 비밀번호 확인
        3. 로그인 성공 시 사용자 정보 반환
        """

        # 이메일로 사용자 찾기 (Model에 위임)
        user = self.user_model.find_by_email(email)

        # 사용자가 없거나 비밀번호가 틀린 경우
        if user is None:
            raise ValueError("*아이디 또는 비밀번호를 확인해주세요")

        # 비교 시 SQLAlchemy ColumnElement가 나올 수 있으므로 문자열로 변환하여 비교
        if str(getattr(user, "password", None)) != password:
            raise ValueError("*아이디 또는 비밀번호를 확인해주세요")

        # 로그인 성공: 비밀번호를 제외한 사용자 정보 반환
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "profile_image": user.profile_image
        }


    # ==================== READ ====================

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """
        사용자 정보 조회 (내부용 - 다른 Controller에서 사용)

        Args:
        - user_id (int): 사용자 ID

        Returns:
        - Optional[Dict]: 사용자 정보 (비밀번호 제외)
        """
        user = self.user_model.find_by_id(user_id)
        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "profile_image": user.profile_image
        }


    # ==================== UPDATE ====================

    def update_nickname(self, user_id: int, new_nickname: str) -> Dict:
        """
        닉네임 수정

        Args:
        - user_id (int): 사용자 ID
        - new_nickname (str): 새 닉네임

        Returns:
        - Dict: 수정된 사용자 정보

        Raises:
        - ValueError: 사용자가 존재하지 않거나 닉네임 중복 시

        Note:
        - CASCADE UPDATE는 데이터베이스에서 ORM relationship으로 자동 처리
        """
        # 사용자 찾기
        user = self.user_model.find_by_id(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다")

        # 현재 닉네임과 동일한 경우는 허용
        if str(getattr(user, "nickname", None)) == new_nickname:
            return {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "profile_image": user.profile_image
            }
        
        # 닉네임 중복 확인 (다른 사용자와 중복)
        existing_user = self.user_model.find_by_nickname(new_nickname)
        # Avoid evaluating SQL expression truthiness (ColumnElement) which raises; check for None explicitly
        if existing_user is not None and getattr(existing_user, "id", None) != user_id:
            raise ValueError("*중복된 닉네임 입니다.")

        # 닉네임 업데이트 (Model에 위임)
        updated_user = self.user_model.update(user_id, nickname=new_nickname)

        if not updated_user:
            updated_user = user  # Fallback to original user if update failed for some reason
            
        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "nickname": updated_user.nickname,
            "profile_image": updated_user.profile_image
        }


    # ==================== DELETE ====================

    def delete_user(self, user_id: int) -> None:
        """
        회원 탈퇴

        Args:
        - user_id (int): 사용자 ID

        Raises:
        - ValueError: 사용자가 존재하지 않을 때

        Note:
        - CASCADE DELETE: 데이터베이스에서 ORM 설정으로 자동 처리
        - 사용자 삭제 시 게시글, 댓글, 좋아요도 자동 삭제됨
        """
        # 사용자 존재 확인
        user = self.user_model.find_by_id(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다")

        # 사용자 삭제 (Model에 위임)
        # CASCADE DELETE로 게시글, 댓글도 자동 삭제
        if not self.user_model.delete(user_id):
            raise ValueError("사용자 삭제에 실패했습니다")
