"""
Post Model

역할:
1. 데이터 접근 계층: 게시글 In-memory 저장소 관리
2. CRUD 연산: 게시글 생성, 조회, 수정, 삭제
3. 관계 데이터 관리: 좋아요, 조회수, 댓글 수 추적

설계 원칙:
- Repository 패턴: 데이터 소스 추상화
- 단일 책임 원칙(SRP): 데이터 접근만 담당
- 불변성: ID는 수정 불가

Note:
- In-memory 저장소 (서버 재시작 시 데이터 소실)
- 프로덕션: SQLAlchemy ORM + PostgreSQL/MySQL 권장
"""

from typing import List, Dict, Optional, Set
from datetime import datetime


class PostModel:
    """
    게시글 데이터 접근 계층

    Attributes:
    - posts (List[Dict]): In-memory 게시글 저장소
    - user_likes (Dict[int, Set[int]]): 사용자별 좋아요한 게시글 추적

    Methods:
    - create: 게시글 생성
    - find_by_id: ID로 게시글 조회
    - find_all: 전체 게시글 조회
    - update: 게시글 수정
    - delete: 게시글 삭제
    - delete_by_author: 특정 작성자의 모든 게시글 삭제
    - increment_views: 조회수 증가
    - toggle_like: 좋아요 토글
    - is_liked_by_user: 사용자의 좋아요 여부 확인
    - increment_comment_count: 댓글 수 증가
    - decrement_comment_count: 댓글 수 감소
    """

    def __init__(self):
        """Model 초기화"""
        self.posts: List[Dict] = []
        self.user_likes: Dict[int, Set[int]] = {}  # {user_id: {post_id, ...}}
        self._next_id: int = 1  # 다음 게시글 ID를 추적하는 카운터


    # ==================== CREATE ====================

    def create(self, title: str, content: str, author_id: int,
               author_nickname: str, author_profile_image: Optional[str],
               image_url: Optional[str] = None) -> Dict:
        """
        게시글 생성

        Args:
        - title (str): 제목
        - content (str): 내용
        - author_id (int): 작성자 ID
        - author_nickname (str): 작성자 닉네임
        - author_profile_image (Optional[str]): 작성자 프로필 이미지
        - image_url (Optional[str]): 게시글 이미지 URL

        Returns:
        - Dict: 생성된 게시글 정보

        Note:
        - ID는 삭제 후에도 중복되지 않도록 _next_id 카운터 사용
        """
        new_post = {
            "id": self._next_id,
            "title": title,
            "content": content,
            "image_url": image_url,
            "author_id": author_id,
            "author_nickname": author_nickname,
            "author_profile_image": author_profile_image,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "views": 0,
            "likes": 0,
            "comment_count": 0
        }
        self.posts.append(new_post)
        self._next_id += 1  # 다음 ID를 위해 증가
        return new_post


    # ==================== READ ====================

    def find_by_id(self, post_id: int) -> Optional[Dict]:
        """
        ID로 게시글 조회

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - Optional[Dict]: 게시글 정보 (없으면 None)
        """
        return next((p for p in self.posts if p["id"] == post_id), None)


    def find_all(self) -> List[Dict]:
        """
        전체 게시글 조회 (최신순 정렬)

        Returns:
        - List[Dict]: 전체 게시글 목록
        """
        return sorted(self.posts, key=lambda x: x["created_at"], reverse=True)


    def find_by_author(self, author_id: int) -> List[Dict]:
        """
        작성자별 게시글 조회

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - List[Dict]: 해당 작성자의 게시글 목록
        """
        return [p for p in self.posts if p["author_id"] == author_id]


    # ==================== UPDATE ====================

    def update(self, post_id: int, **kwargs) -> Optional[Dict]:
        """
        게시글 수정

        Args:
        - post_id (int): 게시글 ID
        - **kwargs: 수정할 필드들 (title, content, image_url)

        Returns:
        - Optional[Dict]: 수정된 게시글 (없으면 None)
        """
        for i, post in enumerate(self.posts):
            if post["id"] == post_id:
                # ID, author_id, created_at 등은 수정 불가
                immutable_fields = {"id", "author_id", "author_nickname",
                                    "author_profile_image", "created_at",
                                    "views", "likes", "comment_count"}

                for key, value in kwargs.items():
                    if key not in immutable_fields and value is not None:
                        self.posts[i][key] = value

                return self.posts[i]

        return None


    def increment_views(self, post_id: int) -> bool:
        """
        조회수 증가

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - bool: 성공 여부
        """
        for post in self.posts:
            if post["id"] == post_id:
                post["views"] += 1
                return True
        return False


    def increment_comment_count(self, post_id: int) -> bool:
        """
        댓글 수 증가

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - bool: 성공 여부
        """
        for post in self.posts:
            if post["id"] == post_id:
                post["comment_count"] += 1
                return True
        return False


    def decrement_comment_count(self, post_id: int) -> bool:
        """
        댓글 수 감소

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - bool: 성공 여부
        """
        for post in self.posts:
            if post["id"] == post_id:
                post["comment_count"] = max(0, post["comment_count"] - 1)
                return True
        return False


    # ==================== LIKE ====================

    def toggle_like(self, post_id: int, user_id: int) -> Optional[tuple[Dict, bool]]:
        """
        좋아요 토글

        Args:
        - post_id (int): 게시글 ID
        - user_id (int): 사용자 ID

        Returns:
        - Optional[tuple[Dict, bool]]: (업데이트된 게시글, 좋아요 상태)
        """
        post = self.find_by_id(post_id)
        if not post:
            return None

        # user_likes 초기화
        if user_id not in self.user_likes:
            self.user_likes[user_id] = set()

        # 토글
        if post_id in self.user_likes[user_id]:
            # 좋아요 취소
            self.user_likes[user_id].remove(post_id)
            post["likes"] = max(0, post["likes"] - 1)
            return (post, False)
        else:
            # 좋아요
            self.user_likes[user_id].add(post_id)
            post["likes"] += 1
            return (post, True)


    def is_liked_by_user(self, post_id: int, user_id: int) -> bool:
        """
        사용자의 좋아요 여부 확인

        Args:
        - post_id (int): 게시글 ID
        - user_id (int): 사용자 ID

        Returns:
        - bool: 좋아요 여부
        """
        return user_id in self.user_likes and post_id in self.user_likes[user_id]


    # ==================== DELETE ====================

    def delete(self, post_id: int) -> bool:
        """
        게시글 삭제

        Args:
        - post_id (int): 게시글 ID

        Returns:
        - bool: 삭제 성공 여부
        """
        for i, post in enumerate(self.posts):
            if post["id"] == post_id:
                self.posts.pop(i)

                # 관련 좋아요 데이터도 삭제
                for user_id in self.user_likes:
                    self.user_likes[user_id].discard(post_id)

                return True

        return False


    def delete_by_author(self, author_id: int) -> List[int]:
        """
        특정 작성자의 모든 게시글 삭제

        Args:
        - author_id (int): 작성자 ID

        Returns:
        - List[int]: 삭제된 게시글 ID 목록
        """
        deleted_ids = []
        self.posts = [
            p for p in self.posts
            if not (p["author_id"] == author_id and deleted_ids.append(p["id"]) is None)
        ]

        # 삭제된 게시글의 좋아요 데이터도 제거
        for user_id in self.user_likes:
            for post_id in deleted_ids:
                self.user_likes[user_id].discard(post_id)

        return deleted_ids
