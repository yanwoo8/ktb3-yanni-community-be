#!/bin/bash

# AI 댓글 생성 디버깅 스크립트

# 한글 깨짐 방지를 위한 함수 정의
pretty_json() {
  python3 -c 'import sys, json; print(json.dumps(json.loads(sys.stdin.read()), indent=2, ensure_ascii=False))'
}

echo "===== AI 댓글 생성 테스트 시작 ====="
echo ""

echo "1. 데이터베이스 초기화..."
curl -X POST http://localhost:8000/dev/reset -s | pretty_json
echo -e "\n"

echo "2. 테스트 사용자 생성..."
REGISTER_RESPONSE=$(curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test1234!",
    "password_confirm": "Test1234!",
    "nickname": "테스터",
    "profile_image": "https://example.com/profile.jpg"
  }' -s)

echo "$REGISTER_RESPONSE" | pretty_json
echo -e "\n"

# 사용자 ID 추출
USER_ID=$(echo "$REGISTER_RESPONSE" | python3 -c 'import sys, json; data=json.load(sys.stdin); print(data.get("data", {}).get("id", 1))' 2>/dev/null || echo "1")
echo "생성된 사용자 ID: $USER_ID"
echo ""

echo "3. 게시글 생성 (AI 댓글 자동 생성됨)..."
POST_RESPONSE=$(curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"FastAPI와 AI 통합 테스트\",
    \"content\": \"OpenRouter를 사용해서 무료로 LLM 모델을 서빙하는 테스트입니다!\",
    \"author_id\": $USER_ID
  }" -s)

echo "$POST_RESPONSE" | pretty_json
echo -e "\n"

# 게시글 ID 추출
POST_ID=$(echo "$POST_RESPONSE" | python3 -c 'import sys, json; data=json.load(sys.stdin); print(data.get("data", {}).get("id", 1))' 2>/dev/null || echo "1")
echo "생성된 게시글 ID: $POST_ID"
echo ""

echo "4. AI 댓글 생성 대기 (10초)..."
sleep 10
echo ""

echo "5. 게시글 댓글 목록 조회..."
curl -X GET "http://localhost:8000/posts/$POST_ID/comments" -s | pretty_json
echo -e "\n"

echo "6. 게시글 상세 조회 (comment_count 확인)..."
curl -X GET "http://localhost:8000/posts/$POST_ID" -s | pretty_json
echo ""

echo "===== 테스트 완료 ====="
echo ""
echo "서버 로그를 확인하여 AI 댓글 생성 과정을 확인하세요."
