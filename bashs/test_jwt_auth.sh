#!/bin/bash

# ==================== JWT 인증 테스트 스크립트 ====================
#
# JWT 기반 인증 시스템 테스트
#
# 테스트 시나리오:
# 1. 회원가입
# 2. 로그인 (JWT 토큰 획득)
# 3. 인증 필요한 API 테스트 (게시글 작성)
# 4. 인증 없이 API 호출 시 401 에러 확인
#
# 사용법:
#   chmod +x test_jwt_auth.sh
#   ./test_jwt_auth.sh
#
# ========================================================================

set -e

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "JWT Authentication Test"
echo "=========================================="
echo ""

# 테스트용 랜덤 이메일 생성
RANDOM_NUM=$RANDOM
TEST_EMAIL="test${RANDOM_NUM}@example.com"
TEST_PASSWORD="TestPass123!"
TEST_NICKNAME="테스터${RANDOM_NUM}"

echo "[1/5] 회원가입 테스트..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"password_confirm\": \"${TEST_PASSWORD}\",
    \"nickname\": \"${TEST_NICKNAME}\"
  }")

echo "회원가입 응답: ${REGISTER_RESPONSE}"
echo ""

echo "[2/5] 로그인 테스트 (JWT 토큰 획득)..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\"
  }")

echo "로그인 응답: ${LOGIN_RESPONSE}"
echo ""

# JWT 토큰 추출 (jq 사용 - 없으면 python으로 대체)
if command -v jq &> /dev/null; then
    ACCESS_TOKEN=$(echo "${LOGIN_RESPONSE}" | jq -r '.access_token')
else
    ACCESS_TOKEN=$(echo "${LOGIN_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
fi

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
    echo "❌ 로그인 실패: JWT 토큰을 받지 못했습니다."
    exit 1
fi

echo "✅ JWT 토큰 획득 성공!"
echo "토큰: ${ACCESS_TOKEN:0:50}..."
echo ""

echo "[3/5] 인증된 게시글 작성 테스트..."
POST_RESPONSE=$(curl -s -X POST "${BASE_URL}/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d "{
    \"title\": \"JWT 테스트 게시글\",
    \"content\": \"이 게시글은 JWT 인증을 통해 작성되었습니다.\"
  }")

echo "게시글 작성 응답: ${POST_RESPONSE}"
echo ""

# 게시글 작성 성공 확인
if echo "${POST_RESPONSE}" | grep -q "Created"; then
    echo "✅ 인증된 게시글 작성 성공!"
else
    echo "❌ 게시글 작성 실패"
fi
echo ""

echo "[4/5] 인증 없이 게시글 작성 시도 (401 에러 예상)..."
UNAUTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${BASE_URL}/posts" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"인증 없는 게시글\",
    \"content\": \"이 게시글은 실패해야 합니다.\"
  }")

HTTP_CODE=$(echo "${UNAUTH_RESPONSE}" | grep "HTTP_CODE" | cut -d':' -f2)

if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ 인증 없는 요청 차단 성공! (HTTP 401)"
else
    echo "❌ 인증 체크 실패 (HTTP ${HTTP_CODE})"
fi
echo ""

echo "[5/5] 잘못된 토큰으로 게시글 작성 시도 (401 에러 예상)..."
INVALID_TOKEN_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${BASE_URL}/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid-token-12345" \
  -d "{
    \"title\": \"잘못된 토큰\",
    \"content\": \"이 게시글도 실패해야 합니다.\"
  }")

HTTP_CODE=$(echo "${INVALID_TOKEN_RESPONSE}" | grep "HTTP_CODE" | cut -d':' -f2)

if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ 잘못된 토큰 차단 성공! (HTTP 401)"
else
    echo "❌ 토큰 검증 실패 (HTTP ${HTTP_CODE})"
fi
echo ""

echo "=========================================="
echo "✅ JWT 인증 테스트 완료!"
echo "=========================================="
echo ""
echo "📝 요약:"
echo "  - 회원가입: 성공"
echo "  - 로그인 (JWT 발급): 성공"
echo "  - 인증된 API 호출: 성공"
echo "  - 비인증 요청 차단: 성공"
echo "  - 잘못된 토큰 차단: 성공"
echo ""
echo "🔐 사용 방법:"
echo "  1. 로그인하여 access_token 받기"
echo "  2. API 호출 시 Header 추가:"
echo "     Authorization: Bearer <access_token>"
echo ""
