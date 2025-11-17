"""
Comment Controller

역할:
1. 비즈니스 로직 처리: 댓글 CRUD 연산
2. Model 계층 호출: 데이터 접근은 CommentModel에 위임
3. 예외 처리: 비즈니스 규칙 위반 시 예외 발생

설계 원칙:
- 단일 책임 원칙(SRP): 댓글 관련 비즈니스 로직만 담당
- 의존성 역전 원칙(DIP): HTTP 계층 및 데이터 계층과 독립적
- Repository 패턴: Model을 통한 데이터 접근

Note:
- Controller → Model → Data 계층 분리
- UserController, PostController 의존성: 관련 정보 조회/업데이트용
"""

from typing import List, Dict
from app.models.comment_model import CommentModel


class CommentController:
    """
    댓글 비즈니스 로직을 담당하는 Controller

    Attributes:
    - comment_model (CommentModel): 댓글 데이터 접근 계층
    - user_controller: 사용자 정보 조회용
    - post_controller: 게시글 댓글수 업데이트용

    Methods:
    - create: 댓글 생성
    - get_by_post_id: 게시글별 댓글 조회
    - get_by_id: 특정 댓글 조회
    - update: 댓글 수정
    - delete: 댓글 삭제
    """

    def __init__(self, comment_model: CommentModel,
                 user_controller=None, post_controller=None):
        """
        Controller 초기화

        Args:
        - comment_model (CommentModel): 의존성 주입된 CommentModel 인스턴스
        - user_controller: 작성자 정보 조회용 (선택)
        - post_controller: 댓글수 업데이트용 (선택)
        """
        self.comment_model = comment_model
        self.user_controller = user_controller
        self.post_controller = post_controller


    # ==================== CREATE ====================

    def create(self, post_id: int, author_id: int, content: str) -> Dict:
        """
        댓글 생성

        Args:
        - post_id (int): 게시글 ID
        - author_id (int): 작성자 ID
        - content (str): 댓글 내용

        Returns:
        - Dict: 생성된 댓글 정보

        Raises:
        - ValueError: 작성자가 존재하지 않을 때

        Business Logic:
        - 작성자 정보 조회 (UserController)
        - 댓글 생성 (CommentModel)
        - 게시글 댓글수 증가 (PostController)
        """
        # 게시글 정보 조회
        is_post_exist = True
        if self.post_controller:
            try:
                self.post_controller.get_by_id(post_id)
            except ValueError:
                is_post_exist = False
        if not is_post_exist:
            raise ValueError(f"게시글 ID {post_id}를 찾을 수 없습니다")
        
        # 작성자 정보 조회
        if self.user_controller:
            author = self.user_controller.get_user_info(author_id)
            if not author:
                raise ValueError(f"작성자 ID {author_id}를 찾을 수 없습니다")
            
            author_nickname = author["nickname"]
            author_profile_image = author.get("profile_image")

        else:
            raise ValueError(f"작성자 ID {author_id}를 찾을 수 없습니다")
            #author_nickname = "Unknown"
            #author_profile_image = None

        # 댓글 생성 (Model에 위임)
        new_comment = self.comment_model.create(
            post_id=post_id,
            author_id=author_id,
            author_nickname=author_nickname,
            author_profile_image=author_profile_image,
            content=content
        )

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
        - List[Dict]: 댓글 목록 (오래된 순)
        """
        return self.comment_model.find_by_post(post_id)


    def get_by_id(self, comment_id: int) -> Dict:
        """
        특정 댓글 조회

        Args:
        - comment_id (int): 댓글 ID

        Returns:
        - Dict: 댓글 정보

        Raises:
        - ValueError: 댓글이 존재하지 않을 때
        """
        comment = self.comment_model.find_by_id(comment_id)

        if not comment:
            raise ValueError(f"댓글 ID {comment_id}가 존재하지 않습니다")

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
        - Dict: 수정된 댓글

        Raises:
        - ValueError: 댓글이 존재하지 않거나 작성자가 아닐 때
        """
        # 댓글 존재 확인
        comment = self.get_by_id(comment_id)

        # 작성자 확인
        if comment["author_id"] != user_id:
            raise ValueError("본인이 작성한 댓글만 수정할 수 있습니다")

        # 댓글 수정 (Model에 위임)
        updated_comment = self.comment_model.update(comment_id, content)

        if not updated_comment:
            raise ValueError(f"댓글 수정에 실패했습니다")

        return updated_comment


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
        # 댓글 존재 확인
        comment = self.get_by_id(comment_id)

        # 작성자 확인
        if comment["author_id"] != user_id:
            raise ValueError("본인이 작성한 댓글만 삭제할 수 있습니다")

        post_id = comment["post_id"]

        # 댓글 삭제 (Model에 위임)
        if not self.comment_model.delete(comment_id):
            raise ValueError(f"댓글 삭제에 실패했습니다")

        # 게시글의 댓글수 감소
        if self.post_controller:
            self.post_controller.decrement_comment_count(post_id)
