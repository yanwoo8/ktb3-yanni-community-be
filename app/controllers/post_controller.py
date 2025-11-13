"""
Post Controller

역할:
1. 비즈니스 로직 처리: CRUD 연산의 실제 구현
2. 데이터 관리: In-memory 저장소 관리
3. 예외 처리: 비즈니스 규칙 위반 시 예외 발생

설계 원칙:
- 단일 책임 원칙(SRP): 게시글 관련 로직만 담당
- 의존성 역전 원칙(DIP): HTTP 계층과 독립적으로 동작
- 인터페이스 분리: Route는 Controller의 public 메서드만 호출

Note:
- 실제 프로덕션에서는 Repository 패턴으로 DB 접근 계층 분리
- 현재는 In-memory 저장소로 구현 (서버 재시작 시 데이터 소실)
"""


from typing import List, Dict, Optional




class PostController:
    """
    게시글 비즈니스 로직을 담당하는 Controller
    
    Attributes:
    - posts (List[Dict]): In-memory 게시글 저장소
    
    Methods:
    - create: 게시글 생성
    - get_all: 전체 게시글 조회
    - get_by_id: 특정 게시글 조회
    - update: 게시글 전체 교체
    - partial_update: 게시글 부분 수정
    - delete: 게시글 삭제
    """
    
    def __init__(self):
        """
        Controller 초기화
        
        Note:
        - Singleton 패턴으로 구현 시 앱 전역에서 하나의 인스턴스만 사용
        - 현재는 FastAPI의 Dependency Injection으로 관리
        """
        self.posts: List[Dict] = []  # In-memory 저장소
    

    # ==================== CREATE ====================


    def create(self, title: str, content: str) -> Dict:
        """
        게시글 생성 (CREATE)
        
        Args:
        - title (str): 게시글 제목
        - content (str): 게시글 내용
        
        Returns:
        - Dict: 생성된 게시글 데이터 (id, title, content 포함)
        
        Business Logic:
        - Auto-increment ID 생성: len(posts) + 1
        - Memory 저장소에 추가 후 생성된 데이터 반환
        """
        new_post = {
            "id": len(self.posts) + 1,
            "title": title,
            "content": content
        }
        self.posts.append(new_post)
        return new_post
    

    # ==================== READ ====================

    
    def get_all(self) -> List[Dict]:
        """
        전체 게시글 조회 (READ ALL)
        
        Returns:
        - List[Dict]: 전체 게시글 목록 (empty: [])
        
        Note:
        - 이후 Pagination, Filtering, Sorting 구현 필요
        """
        return self.posts
    
    

    def get_by_id(self, post_id: int) -> Dict:
        """
        특정 게시글 조회 (READ ONE)
        
        Args:
        - post_id (int): 조회할 게시글 ID
        
        Returns:
        - Dict: 조회된 게시글 데이터
        
        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        
        Note:
        - next(): Generator에서 첫 번째 일치 항목 반환
        - 없으면 None 반환 → ValueError 발생
        """
        post = next((p for p in self.posts if p["id"] == post_id), None)
        
        if not post:
            raise ValueError(f"Post with id {post_id} does not exist")
        
        return post
    

    # ==================== UPDATE ====================
    
    
    def update(self, post_id: int, title: str, content: str) -> Dict:
        """
        게시글 전체 교체 (UPDATE - PUT)
        
        Args:
        - post_id (int): 수정할 게시글 ID
        - title (str): 새 제목
        - content (str): 새 내용
        
        Returns:
        - Dict: 수정된 게시글 데이터
        
        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        
        Business Logic:
        - ID는 유지, 나머지 필드는 전체 교체
        - PUT의 Idempotent 특성: 같은 요청 반복 시 동일한 결과
        """
        for i, p in enumerate(self.posts):
            if p["id"] == post_id:
                updated_post = {
                    "id": post_id,
                    "title": title,
                    "content": content
                }
                self.posts[i] = updated_post
                return updated_post
        
        raise ValueError(f"Post with id {post_id} does not exist")
    
    

    def partial_update(self, post_id: int, title: Optional[str] = None, 
                       content: Optional[str] = None) -> Dict:
        """
        게시글 부분 수정 (UPDATE - PATCH)
        
        Args:
        - post_id (int): 수정할 게시글 ID
        - title (Optional[str]): 새 제목 (선택)
        - content (Optional[str]): 새 내용 (선택)
        
        Returns:
        - Dict: 수정된 게시글 데이터
        
        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        
        Business Logic:
        - None이 아닌 필드만 업데이트
        - 기존 값은 유지
        """
        for i, p in enumerate(self.posts):
            if p["id"] == post_id:
                # None이 아닌 필드만 업데이트
                if title is not None:
                    self.posts[i]["title"] = title
                if content is not None:
                    self.posts[i]["content"] = content
                
                return self.posts[i]
        
        raise ValueError(f"Post with id {post_id} does not exist")
    

    # ==================== DELETE ====================
    

    def delete(self, post_id: int) -> None:
        """
        게시글 삭제 (DELETE)
        
        Args:
        - post_id (int): 삭제할 게시글 ID
        
        Raises:
        - ValueError: 게시글이 존재하지 않을 때
        
        Business Logic:
        - Hard Delete: 실제 데이터 삭제
        - 실제 프로덕션: Soft Delete (deleted_at 플래그) 권장
        """
        for i, p in enumerate(self.posts):
            if p["id"] == post_id:
                self.posts.pop(i)
                return # None
        
        raise ValueError(f"Post with id {post_id} does not exist")