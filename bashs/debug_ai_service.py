#!/usr/bin/env python3
"""
AI Service Debug Script
AI 댓글 서비스 디버깅 도구
"""

import asyncio
import os
from dotenv import load_dotenv

print("=" * 60)
print("AI Service Debug")
print("=" * 60)
print()

# 1. 환경변수 로드
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY", "")
print(f"1. 환경변수 확인")
print(f"   API 키 존재: {bool(api_key)}")
print(f"   API 키 길이: {len(api_key)}")
print()

# 2. YAML 설정 로드
try:
    from app.utils.config_loader import get_cached_ai_service_config, get_current_model_config

    config = get_cached_ai_service_config()
    model_config = get_current_model_config(config)

    print(f"2. YAML 설정 로드")
    print(f"   ✅ 성공")
    print(f"   현재 모델: {model_config['name']}")
    print(f"   모델 ID: {model_config['id']}")
    print()
except Exception as e:
    print(f"2. YAML 설정 로드")
    print(f"   ❌ 실패: {type(e).__name__} - {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    exit(1)

# 3. AI 서비스 초기화
try:
    from app.services.ai_comment_service import AICommentService

    service = AICommentService()

    print(f"3. AI 서비스 초기화")
    print(f"   ✅ 성공")
    print(f"   모델: {service.model_name}")
    print(f"   API URL: {service.api_url}")
    print(f"   타임아웃: {service.timeout}초")
    print()
except Exception as e:
    print(f"3. AI 서비스 초기화")
    print(f"   ❌ 실패: {type(e).__name__} - {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    exit(1)

# 4. 댓글 생성 테스트
async def test_comment_generation():
    try:
        print(f"4. AI 댓글 생성 테스트")
        print(f"   요청 중...")

        comment = await service.generate_comment(
            "테스트 제목",
            "테스트 내용입니다."
        )

        print(f"   ✅ 성공")
        print(f"   생성된 댓글: \"{comment}\"")
        print()

        if "실패했습니다" in comment:
            print(f"   ⚠️  Fallback 메시지가 반환되었습니다.")
            print(f"   서버 로그를 확인하여 실패 원인을 파악하세요.")

    except Exception as e:
        print(f"   ❌ 실패: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        print()

asyncio.run(test_comment_generation())

print("=" * 60)
print("디버깅 완료")
print("=" * 60)
