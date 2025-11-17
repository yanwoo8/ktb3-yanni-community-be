"""
Comment Model

역할:
1. 데이터 접근 계층: 댓글 In-memory 저장소 관리
2. CRUD 연산: 댓글 생성, 조회, 수정, 삭제
3. 관계 데이터 관리: 게시글별 댓글, 작성자별 댓글 조회

설계 원칙:
- Repository 패턴: 데이터 소스 추상화
- 단일 책임 원칙(SRP): 데이터 접근만 담당
- 참조 무결성: 게시글 삭제 시 댓글도 삭제 (CASCADE)

Note:
- In-memory 저장소 (서버 재시작 시 데이터 소실)
- 프로덕션: ORM + Foreign Key Constraint 권장
"""

from typing import List, Dict, Optional
from datetime import datetime


class CommentModel:
    """
    댓글 데이터 접근 계층

    Attributes:
    - comments (List[Dict]): In-memory 댓글 저장소

    Methods:
    - create: 댓글 생성
    - find_by_id: ID로 댓글 조회
    - find_by_post: 게시글별 댓글 조회
    - find_by_author: 작성자별 댓글 조회
    - update: 댓글 수정
    - delete: 댓글 삭제
    - delete_by_post: 게시글의 모든 댓글 삭제
    - delete_by_author: 작성자의 모든 댓글 삭제
    """

    def __init__(self):
        """Model 초기화"""
        self.comments: List[Dict] = []
        self._next_id: int = 1  # 다음 댓글 ID를 추적하는 카운터


    # ==================== CREATE ====================

    def create(self, post_id: int, author_id: int, author_nickname: str,
               author_profile_image: Optional[str], content: str) -> Dict:
        """
        댓글 생성

        Args:
        - post_id (int): 게시글 ID
        - author_id (int): 작성자 ID
        - author_nickname (str): 작성자 닉네임
        - author_profile_image (Optional[str]): 작성자 프로필 이미지
        - content (str): 댓글 내용

        Returns:
        - Dict: 생성된 댓글 정보

        Note:
        - ID는 삭제 후에도 중복되지 않도록 _next_id 카운터 사용
        """
        new_comment = {
            "id": self._next_id,
            "post_id": post_id,
            "author_id": author_id,
            "author_nickname": author_nickname,
            "author_profile_image": author_profile_image,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.comments.append(new_comment)
        self._next_id += 1  # 다음 ID를 위해 증가
        return new_comment


    # ==================== READ ====================

    def find_by_id(self, comment_id: int) -> Optional[Dict]:
        """
        ID로 댓글 조회

        Args:
        - comment_id (int): 댓글 ID

        Returns:
        - Optional[Dict]: 댓글 정보 (없으면 None)
        """
        return next((c for c in self.comments if c["id"] == comment_id), None)


    def find_by_post(self, post_id: int) -> List[Dict]:
        """
        게시글별 댓글 조회 (오래된 순)

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - List[Dict]: 댓글 목록
        """
        return sorted(
            [c for c in self.comments if c["post_id"] == post_id],
            key=lambda x: x["created_at"]
        )


    def find_by_author(self, author_id: int) -> List[Dict]:
        """
        작성자별 댓글 조회

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - List[Dict]: 댓글 목록
        """
        return [c for c in self.comments if c["author_id"] == author_id]


    # ==================== UPDATE ====================

    def update(self, comment_id: int, content: str) -> Optional[Dict]:
        """
        댓글 수정

        Args:
        - comment_id (int): 댓글 ID
        - content (str): 새 댓글 내용

        Returns:
        - Optional[Dict]: 수정된 댓글 (없으면 None)
        """
        for i, comment in enumerate(self.comments):
            if comment["id"] == comment_id:
                self.comments[i]["content"] = content
                return self.comments[i]

        return None


    # ==================== DELETE ====================

    def delete(self, comment_id: int) -> bool:
        """
        댓글 삭제

        Args:
        - comment_id (int): 댓글 ID

        Returns:
        - bool: 삭제 성공 여부
        """
        for i, comment in enumerate(self.comments):
            if comment["id"] == comment_id:
                self.comments.pop(i)
                return True

        return False


    def delete_by_post(self, post_id: int) -> int:
        """
        게시글의 모든 댓글 삭제 (CASCADE)

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - int: 삭제된 댓글 수
        """
        initial_count = len(self.comments)
        self.comments = [c for c in self.comments if c["post_id"] != post_id]
        return initial_count - len(self.comments)


    def delete_by_author(self, author_id: int) -> int:
        """
        작성자의 모든 댓글 삭제

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - int: 삭제된 댓글 수
        """
        initial_count = len(self.comments)
        self.comments = [c for c in self.comments if c["author_id"] != author_id]
        return initial_count - len(self.comments)
