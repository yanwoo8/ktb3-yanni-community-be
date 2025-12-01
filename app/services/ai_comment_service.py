"""
AI Comment Service

역할:
1. LLM API를 활용한 자동 댓글 생성
2. 게시글 내용 분석 및 적절한 첫 댓글 작성
3. 비동기 처리를 통한 게시글 생성 성능 최적화

기술 스택:
- OpenRouter API (무료 모델 제공)
- 모델: google/gemini-2.0-flash-exp:free (빠르고 성능 좋은 무료 모델)
- 비동기 HTTP 클라이언트: httpx

설계:
- 백그라운드 작업: 게시글 생성 후 비동기로 AI 댓글 추가
- 에러 핸들링: AI 생성 실패 시 fallback 메시지 사용
- AI 모델 서빙: OpenRouter를 통한 다양한 모델 접근
"""

import os
import httpx
import asyncio
from typing import Optional
import logging

# 로깅 설정
logger = logging.getLogger(__name__)


class AICommentService:
    """
    AI 댓글 자동 생성 서비스 (OpenRouter 활용)

    Attributes:
    - api_url: OpenRouter API URL
    - headers: API 인증 헤더
    - model: 사용할 LLM 모델
    - timeout: API 요청 타임아웃 (초)

    Methods:
    - generate_comment: 게시글에 대한 AI 댓글 생성
    - _call_llm_api: LLM API 호출
    - _create_messages: 채팅 메시지 생성
    """

    def __init__(self, api_token: Optional[str] = None):
        """
        서비스 초기화

        Args:
        - api_token: OpenRouter API 토큰 (환경변수 또는 직접 입력)
        """
        self.api_token = api_token or os.getenv("OPENROUTER_API_KEY", "")

        # OpenRouter API 설정
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # 무료 모델 옵션 (rate limit 발생 시 다른 모델로 변경)
        # 1. google/gemini-2.0-flash-exp:free - 빠르지만 rate limit 가능
        # 2. meta-llama/llama-3.2-3b-instruct:free - 안정적
        # 3. google/gemini-flash-1.5:free - 안정적인 Gemini 구버전
        self.model = "meta-llama/llama-3.2-3b-instruct:free"

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yanwoo8/ktb3-yanni-community-be",  # OpenRouter 요구사항
            "X-Title": "Community Backend AI Comment"  # OpenRouter 요구사항
        }

        # API 타임아웃 설정 (30초)
        self.timeout = 30.0

        # Fallback 메시지 (API 실패 시 사용)
        self.fallback_message = "AI 댓글 생성에 실패했습니다. 나중에 다시 시도해주세요."


    async def generate_comment(self, post_title: str, post_content: str) -> str:
        """
        게시글에 대한 AI 댓글 생성

        Args:
        - post_title: 게시글 제목
        - post_content: 게시글 내용

        Returns:
        - str: 생성된 댓글 내용

        Note:
        - API 실패 시 fallback 메시지 반환
        - 비동기 처리로 성능 최적화
        """
        try:
            logger.info(f"AI 댓글 생성 시작 - 제목: {post_title[:30]}...")

            # API 토큰 확인
            if not self.api_token:
                logger.warning("OpenRouter API 토큰이 설정되지 않았습니다. Fallback 메시지를 사용합니다.")
                return self._get_fallback_message()

            logger.info(f"API 토큰 확인 완료 (길이: {len(self.api_token)})")

            # 메시지 생성
            messages = self._create_messages(post_title, post_content)
            logger.info(f"프롬프트 메시지 생성 완료")

            # LLM API 호출
            logger.info(f"OpenRouter API 호출 시작 (모델: {self.model})")
            comment = await self._call_llm_api(messages)
            logger.info(f"API 호출 완료 - 생성된 댓글 길이: {len(comment) if comment else 0}")

            # 댓글 검증 및 정제
            if comment and len(comment.strip()) > 5:
                logger.info(f"AI 댓글 생성 성공: {comment[:50]}...")
                return comment.strip()
            else:
                logger.warning("생성된 댓글이 너무 짧습니다. Fallback 메시지를 사용합니다.")
                return self._get_fallback_message()

        except Exception as e:
            logger.error(f"AI 댓글 생성 실패: {type(e).__name__} - {str(e)}", exc_info=True)
            return self._get_fallback_message()


    async def _call_llm_api(self, messages: list) -> str:
        """
        OpenRouter API 호출

        Args:
        - messages: 채팅 메시지 리스트

        Returns:
        - str: 생성된 댓글 텍스트

        Raises:
        - Exception: API 호출 실패 시
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,      # 창의성 (0.7 = 적당히 창의적)
            "max_tokens": 150,       # 최대 토큰 수 (짧은 댓글)
            "top_p": 0.9             # 다양성
        }

        logger.info(f"API 요청 페이로드: model={self.model}, messages_count={len(messages)}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )

                logger.info(f"API 응답 상태 코드: {response.status_code}")

                # HTTP 에러 확인
                if response.status_code != 200:
                    logger.error(f"OpenRouter API 호출 실패: {response.status_code} - {response.text}")
                    raise Exception(f"API returned {response.status_code}")

                # 응답 파싱
                result = response.json()
                logger.info(f"API 응답 키: {list(result.keys())}")

                # OpenRouter 응답 형식: {"choices": [{"message": {"content": "..."}}]}
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"]
                    logger.info(f"생성된 텍스트 추출 완료 (길이: {len(generated_text)})")
                    return generated_text
                else:
                    logger.warning(f"예상치 못한 OpenRouter 응답 형식: {result}")
                    raise Exception("Unexpected API response format")

            except httpx.TimeoutException as e:
                logger.error(f"API 호출 타임아웃 ({self.timeout}초): {str(e)}")
                raise Exception(f"API timeout after {self.timeout}s")
            except httpx.HTTPError as e:
                logger.error(f"HTTP 에러: {type(e).__name__} - {str(e)}")
                raise
            except Exception as e:
                logger.error(f"API 호출 중 예외 발생: {type(e).__name__} - {str(e)}")
                raise


    def _create_messages(self, post_title: str, post_content: str) -> list:
        """
        OpenRouter용 채팅 메시지 생성

        Args:
        - post_title: 게시글 제목
        - post_content: 게시글 내용

        Returns:
        - list: OpenRouter 채팅 메시지 형식

        Note:
        - 게시글 요약 댓글
        - 2-3문장의 짧은 댓글
        """
        # 내용이 너무 길면 앞부분만 사용 (토큰 절약)
        content_preview = post_content[:300] if len(post_content) > 300 else post_content

        system_message = {
            "role": "system",
            "content": "당신은 요약 전문가입니다. 게시글 내용을 분석하여 요약한 내용을 작성합니다."
        }

        user_message = {
            "role": "user",
            "content": f"""다음 게시글의 내용을 2~3문장의 한국어로 요약해주세요.

게시글 제목: {post_title}
게시글 내용: {content_preview}

댓글 작성 가이드:
1. 주제에 대한 진심 어린 관심 표현
2. 토론을 유도하는 질문 또는 의견
3. 친근하고 환영하는 분위기

댓글:"""
        }

        return [system_message, user_message]


    def _get_fallback_message(self) -> str:
        """
        Fallback 메시지 반환

        Returns:
        - str: 무작위 fallback 메시지

        Note:
        - API 실패 시 사용
        - 간단하지만 긍정적인 메시지
        """
        return self.fallback_message


# ==================== 싱글톤 인스턴스 ====================

# 전역 서비스 인스턴스 (앱 시작 시 한 번만 생성)
_ai_comment_service_instance: Optional[AICommentService] = None


def get_ai_comment_service() -> AICommentService:
    """
    AI 댓글 서비스 싱글톤 인스턴스 반환

    Returns:
    - AICommentService: 전역 서비스 인스턴스

    Note:
    - 메모리 효율성을 위해 싱글톤 패턴 사용
    - 환경변수에서 API 토큰 자동 로드
    """
    global _ai_comment_service_instance

    if _ai_comment_service_instance is None:
        _ai_comment_service_instance = AICommentService()

    return _ai_comment_service_instance
