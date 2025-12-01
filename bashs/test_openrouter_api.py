#!/usr/bin/env python3
"""
OpenRouter API 직접 테스트 스크립트
AI 댓글 생성이 실패하는 원인을 파악하기 위한 디버깅 도구
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv
from app.services.ai_comment_service import AICommentService

# .env 파일 로드
load_dotenv()

async def test_openrouter_api():
    """OpenRouter API 직접 호출 테스트"""

    # 환경변수에서 API 키 가져오기
    api_token = os.getenv("OPENROUTER_API_KEY", "")

    print("=" * 60)
    print("OpenRouter API 테스트")
    print("=" * 60)
    print()

    # 1. API 키 확인
    print(f"1. API 키 확인")
    print(f"   - 존재 여부: {bool(api_token)}")
    print(f"   - 길이: {len(api_token)}")
    print(f"   - 시작: {api_token[:15] if api_token else '없음'}...")
    print()

    if not api_token:
        print("❌ API 키가 없습니다. .env 파일을 확인해주세요.")
        return

    # 2. API 설정
    AICommentService_instance = AICommentService(api_token=api_token)
    api_url = AICommentService_instance.api_url
    model = AICommentService_instance.model
    headers = AICommentService_instance.headers

    post_name = "테스트 게시글"
    post_content = "이 게시글은 OpenRouter API 테스트를 위해 작성되었습니다."

    message = AICommentService_instance._create_messages(
        post_title=post_name,
        post_content=post_content)
    
    payload = {
        "model": model,
        "messages": message,
        "temperature": 0.7,
        "max_tokens": 300,
        "top_p": 0.9
    }
    
    print(f"2. API 호출 준비")
    print(f"   - URL: {api_url}")
    print(f"   - 모델: {model}")
    print(f"   - 타임아웃: 30초")
    print()

    # 3. API 호출
    print(f"3. API 호출 시작...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=payload
            )

            print(f"   - 상태 코드: {response.status_code}")
            print()

            if response.status_code == 200:
                result = response.json()

                print(f"4. API 응답 성공 ✅")
                print(f"   - 응답 키: {list(result.keys())}")

                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"]
                    print(f"   - 생성된 댓글:")
                    print(f"     \"{generated_text}\"")
                    print()
                    print(f"✅ AI 댓글 생성 성공!")
                else:
                    print(f"   - 예상치 못한 응답 형식:")
                    print(f"     {result}")
                    print()
                    print(f"❌ 응답 형식 오류")

                # 사용량 정보 출력
                if "usage" in result:
                    usage = result["usage"]
                    print()
                    print(f"5. 사용량 정보")
                    print(f"   - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                    print(f"   - Total tokens: {usage.get('total_tokens', 'N/A')}")

            else:
                print(f"4. API 호출 실패 ❌")
                print(f"   - 상태 코드: {response.status_code}")
                print(f"   - 응답 본문:")
                print(f"     {response.text}")

                # 흔한 에러 코드 설명
                if response.status_code == 401:
                    print()
                    print("💡 해결 방법: API 키가 잘못되었거나 만료되었습니다.")
                    print("   - https://openrouter.ai/keys 에서 새 키를 발급받으세요.")
                elif response.status_code == 402:
                    print()
                    print("💡 해결 방법: 크레딧이 부족합니다.")
                    print("   - https://openrouter.ai/credits 에서 크레딧을 충전하세요.")
                    print("   - 또는 무료 모델을 사용하고 있는지 확인하세요.")
                elif response.status_code == 429:
                    print()
                    print("💡 해결 방법: 요청 한도를 초과했습니다.")
                    print("   - 잠시 후 다시 시도하세요.")

    except httpx.TimeoutException as e:
        print(f"❌ 타임아웃 발생 (30초 초과)")
        print(f"   에러: {str(e)}")

    except httpx.HTTPError as e:
        print(f"❌ HTTP 에러 발생")
        print(f"   타입: {type(e).__name__}")
        print(f"   에러: {str(e)}")

    except Exception as e:
        print(f"❌ 예외 발생")
        print(f"   타입: {type(e).__name__}")
        print(f"   에러: {str(e)}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_openrouter_api())
