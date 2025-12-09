#!/bin/bash

# 테스트 스크립트: 로그인 후 게시글 작성

echo "=== 1. 사용자 등록 테스트 ==="
REGISTER_RESPONSE=$(curl -s -X POST 'http://localhost:8000/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "testuser99@test.com",
    "password": "Test1234!",
    "password_confirm": "Test1234!",
    "nickname": "test99"
  }')
echo "$REGISTER_RESPONSE"
echo ""

echo "=== 2. 로그인 테스트 ==="
LOGIN_RESPONSE=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "testuser99@test.com",
    "password": "Test1234!"
  }')
echo "$LOGIN_RESPONSE"
echo ""

# JWT 토큰 추출
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ 로그인 실패: 토큰을 가져올 수 없습니다."
  exit 1
fi

echo "✅ JWT 토큰: $TOKEN"
echo ""

echo "=== 3. 토큰 없이 게시글 작성 시도 (실패해야 함) ==="
curl -s -X POST 'http://localhost:8000/posts' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "테스트 게시글",
    "content": "이것은 테스트 내용입니다"
  }'
echo ""
echo ""

echo "=== 4. JWT 토큰을 포함한 게시글 작성 시도 (성공해야 함) ==="
curl -s -X POST 'http://localhost:8000/posts' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "인증된 게시글",
    "content": "JWT 토큰으로 인증 성공!"
  }'
echo ""
