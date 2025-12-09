"""
Services Package

역할:
- 외부 API 통신 및 복잡한 비즈니스 로직 처리
- Controller와 분리된 서비스 계층
"""

from app.services.ai_comment_service import AICommentService, get_ai_comment_service

__all__ = ["AICommentService", "get_ai_comment_service"]
