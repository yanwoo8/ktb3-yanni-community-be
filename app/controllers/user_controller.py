"""
User Controller

역할:
1. 비즈니스 로직 처리: 회원가입, 로그인 등 사용자 인증 로직
2. 데이터 관리: In-memory 사용자 저장소 관리
3. 예외 처리: 비즈니스 규칙 위반 시 예외 발생

설계 원칙:
- 단일 책임 원칙(SRP): 사용자 인증 관련 로직만 담당
- 의존성 역전 원칙(DIP): HTTP 계층과 독립적으로 동작
- 인터페이스 분리: Route는 Controller의 public 메서드만 호출

Note:
- 실제 프로덕션에서는 Repository 패턴으로 DB 접근 계층 분리
- 현재는 In-memory 저장소로 구현 (서버 재시작 시 데이터 소실)
- 비밀번호는 실제로는 해싱하여 저장해야 함 (bcrypt, argon2 등)
"""

import re
from typing import List, Dict, Optional


class UserController:
    """
    사용자 인증 비즈니스 로직을 담당하는 Controller

    Attributes:
    - users (List[Dict]): In-memory 사용자 저장소

    Methods:
    - register: 회원가입
    - login: 로그인
    - check_email_duplicate: 이메일 중복 확인
    - check_nickname_duplicate: 닉네임 중복 확인
    - update_nickname: 닉네임 수정
    - delete_user: 회원 탈퇴
    """

    def __init__(self):
        """
        Controller 초기화

        Note:
        - Singleton 패턴으로 구현 시 앱 전역에서 하나의 인스턴스만 사용
        - 현재는 FastAPI의 Dependency Injection으로 관리
        """
        self.users: List[Dict] = []  # In-memory 저장소

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
        if self.check_email_duplicate(email):
            raise ValueError("*중복된 이메일입니다")

        # 3. 비밀번호 확인 일치 여부
        if password != password_confirm:
            raise ValueError("*비밀번호가 다릅니다")

        # 4. 닉네임 중복 확인
        if self.check_nickname_duplicate(nickname):
            raise ValueError("*중복된 닉네임 입니다.")

        # 5. 사용자 생성
        new_user = {
            "id": len(self.users) + 1,
            "email": email,
            "password": password,  # 실제로는 해싱하여 저장해야 함
            "nickname": nickname,
            "profile_image": profile_image
        }
        self.users.append(new_user)

        # 비밀번호를 제외한 사용자 정보 반환
        return {
            "id": new_user["id"],
            "email": new_user["email"],
            "nickname": new_user["nickname"],
            "profile_image": new_user["profile_image"]
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

        # 이메일로 사용자 찾기
        user = next((u for u in self.users if u["email"] == email), None)

        # 사용자가 없거나 비밀번호가 틀린 경우
        if not user or user["password"] != password:
            raise ValueError("*아이디 또는 비밀번호를 확인해주세요")

        # 로그인 성공: 비밀번호를 제외한 사용자 정보 반환
        return {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profile_image": user["profile_image"]
        }

    # ==================== VALIDATION ====================

    def check_email_duplicate(self, email: str) -> bool:
        """
        이메일 중복 확인

        Args:
        - email (str): 확인할 이메일

        Returns:
        - bool: 중복이면 True, 아니면 False
        """
        return any(u["email"] == email for u in self.users)

    def check_nickname_duplicate(self, nickname: str) -> bool:
        """
        닉네임 중복 확인

        Args:
        - nickname (str): 확인할 닉네임

        Returns:
        - bool: 중복이면 True, 아니면 False
        """
        return any(u["nickname"] == nickname for u in self.users)


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
        """
        # 사용자 찾기
        user = next((u for u in self.users if u["id"] == user_id), None)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다")

        # 현재 닉네임과 동일한 경우는 허용
        if user["nickname"] == new_nickname:
            return {
                "id": user["id"],
                "email": user["email"],
                "nickname": user["nickname"],
                "profile_image": user["profile_image"]
            }

        # 닉네임 중복 확인 (다른 사용자와 중복)
        if any(u["nickname"] == new_nickname and u["id"] != user_id for u in self.users):
            raise ValueError("*중복된 닉네임 입니다.")

        # 닉네임 업데이트
        user["nickname"] = new_nickname

        return {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profile_image": user["profile_image"]
        }


    # ==================== DELETE ====================

    def delete_user(self, user_id: int, post_controller=None, comment_controller=None) -> None:
        """
        회원 탈퇴

        Args:
        - user_id (int): 사용자 ID
        - post_controller: 게시글 컨트롤러 (사용자의 게시글 삭제용)
        - comment_controller: 댓글 컨트롤러 (사용자의 댓글 삭제용)

        Raises:
        - ValueError: 사용자가 존재하지 않을 때

        Business Logic:
        - 사용자가 작성한 게시글 모두 삭제
        - 사용자가 작성한 댓글 모두 삭제
        - 사용자 정보 삭제
        """
        # 사용자 찾기
        user = next((u for u in self.users if u["id"] == user_id), None)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다")

        # 사용자의 게시글 모두 삭제
        if post_controller:
            user_posts = [p for p in post_controller.posts if p["author_id"] == user_id]
            for post in user_posts:
                post_controller.delete(post["id"])

        # 사용자의 댓글 모두 삭제
        if comment_controller:
            user_comments = [c for c in comment_controller.comments if c["author_id"] == user_id]
            for comment in user_comments[:]:  # 복사본으로 반복
                comment_controller.comments.remove(comment)
                # 댓글수 감소
                if post_controller:
                    try:
                        post_controller.decrement_comment_count(comment["post_id"])
                    except:
                        pass

        # 사용자 삭제
        for i, u in enumerate(self.users):
            if u["id"] == user_id:
                self.users.pop(i)
                return
