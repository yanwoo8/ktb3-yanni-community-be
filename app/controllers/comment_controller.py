"""
Comment Controller

역할:
1. 비즈니스 로직 처리: 댓글 CRUD 연산의 실제 구현
2. 데이터 관리: In-memory 댓글 저장소 관리
3. 예외 처리: 비즈니스 규칙 위반 시 예외 발생

설계 원칙:
- 단일 책임 원칙(SRP): 댓글 관련 로직만 담당
- 의존성 역전 원칙(DIP): HTTP 계층과 독립적으로 동작
- 인터페이스 분리: Route는 Controller의 public 메서드만 호출

Note:
- 실제 프로덕션에서는 Repository 패턴으로 DB 접근 계층 분리
- 현재는 In-memory 저장소로 구현 (서버 재시작 시 데이터 소실)
"""

from typing import List, Dict
from datetime import datetime


class CommentController:
    """
    댓글 비즈니스 로직을 담당하는 Controller

    Attributes:
    - comments (List[Dict]): In-memory 댓글 저장소

    Methods:
    - create: 댓글 생성
    - get_by_post_id: 특정 게시글의 댓글 목록 조회
    - get_by_id: 특정 댓글 조회
    - update: 댓글 수정
    - delete: 댓글 삭제
    """

    def __init__(self, user_controller=None, post_controller=None):
        """
        Controller 초기화

        Note:
        - user_controller: 작성자 정보 조회용
        - post_controller: 댓글수 업데이트용
        """
        self.comments: List[Dict] = []
        self.user_controller = user_controller
        self.post_controller = post_controller


    # ==================== CREATE ====================

    def create(self, post_id: int, author_id: int, content: str) -> Dict:
        """
        댓글 생성 (CREATE)

        Args:
        - post_id (int): 게시글 ID
        - author_id (int): 작성자 ID
        - content (str): 댓글 내용

        Returns:
        - Dict: 생성된 댓글 데이터

        Business Logic:
        - Auto-increment ID 생성
        - 작성일시: 현재 시간
        - 게시글의 댓글수 증가
        """
        # 작성자 정보 확인
        if self.user_controller:
            users = self.user_controller.users
            author = next((u for u in users if u["id"] == author_id), None)
            if not author:
                raise ValueError(f"작성자 ID {author_id}를 찾을 수 없습니다")
            author_nickname = author["nickname"]
            author_profile_image = author.get("profile_image")
        else:
            author_nickname = "Unknown"
            author_profile_image = None

        new_comment = {
            "id": len(self.comments) + 1,
            "post_id": post_id,
            "author_id": author_id,
            "author_nickname": author_nickname,
            "author_profile_image": author_profile_image,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.comments.append(new_comment)

        # 게시글의 댓글수 증가
        if self.post_controller:
            self.post_controller.increment_comment_count(post_id)

        return new_comment


    # ==================== READ ====================

    def get_by_post_id(self, post_id: int) -> List[Dict]:
        """
        특정 게시글의 댓글 목록 조회

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - List[Dict]: 댓글 목록 (작성일시 오름차순)
        """
        post_comments = [c for c in self.comments if c["post_id"] == post_id]
        return sorted(post_comments, key=lambda x: x["id"])


    def get_by_id(self, comment_id: int) -> Dict:
        """
        특정 댓글 조회

        Args:
        - comment_id (int): 댓글 ID

        Returns:
        - Dict: 댓글 데이터

        Raises:
        - ValueError: 댓글이 존재하지 않을 때
        """
        comment = next((c for c in self.comments if c["id"] == comment_id), None)

        if not comment:
            raise ValueError(f"Comment with id {comment_id} does not exist")

        return comment


    # ==================== UPDATE ====================

    def update(self, comment_id: int, content: str, user_id: int) -> Dict:
        """
        댓글 수정

        Args:
        - comment_id (int): 댓글 ID
        - content (str): 새 댓글 내용
        - user_id (int): 수정 요청 사용자 ID

        Returns:
        - Dict: 수정된 댓글 데이터

        Raises:
        - ValueError: 댓글이 존재하지 않거나 작성자가 아닐 때
        """
        comment = self.get_by_id(comment_id)

        # 작성자 확인
        if comment["author_id"] != user_id:
            raise ValueError("본인이 작성한 댓글만 수정할 수 있습니다")

        comment["content"] = content
        return comment


    # ==================== DELETE ====================

    def delete(self, comment_id: int, user_id: int) -> None:
        """
        댓글 삭제

        Args:
        - comment_id (int): 댓글 ID
        - user_id (int): 삭제 요청 사용자 ID

        Raises:
        - ValueError: 댓글이 존재하지 않거나 작성자가 아닐 때

        Business Logic:
        - 작성자만 삭제 가능
        - 게시글의 댓글수 감소
        """
        comment = self.get_by_id(comment_id)

        # 작성자 확인
        if comment["author_id"] != user_id:
            raise ValueError("본인이 작성한 댓글만 삭제할 수 있습니다")

        post_id = comment["post_id"]

        # 댓글 삭제
        for i, c in enumerate(self.comments):
            if c["id"] == comment_id:
                self.comments.pop(i)
                break

        # 게시글의 댓글수 감소
        if self.post_controller:
            self.post_controller.decrement_comment_count(post_id)
