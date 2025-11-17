#!/bin/bash

uvicorn app.main:app

# 한글 깨짐 방지를 위한 함수 정의
pretty_json() {
  local input=$(cat)
  if [ -z "$input" ]; then
    echo "(204 No Content - 삭제 성공)"
  else
    echo "$input" | python3 -c 'import sys, json; print(json.dumps(json.loads(sys.stdin.read()), indent=2, ensure_ascii=False))'
  fi
}

echo ""
echo "===== 데이터 리셋 시작 ====="
echo ""

echo "1. 리셋 전 데이터 상태 확인..."
curl -X GET http://localhost:8000/dev/status -s | pretty_json
echo -e "\n"

echo "2. 모든 데이터 초기화..."
curl -X POST http://localhost:8000/dev/reset -s | pretty_json
echo -e "\n"

echo "3. 리셋 후 데이터 상태 확인..."
curl -X GET http://localhost:8000/dev/status -s | pretty_json
echo -e "\n"

echo "===== 데이터 리셋 완료 ====="
echo ""

echo ""
echo "===== 커뮤니티 백엔드 API 테스트 시작 ====="
echo ""

echo "1. 회원가입 테스트..."
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@test.com",
    "password": "Test1234!",
    "password_confirm": "Test1234!",
    "nickname": "사용자1",
    "profile_image": "https://example.com/user1.jpg"
  }' | pretty_json
echo -e "\n"


echo "2. 두 번째 사용자 회원가입..."
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user2@test.com",
    "password": "Test5678!",
    "password_confirm": "Test5678!",
    "nickname": "사용자2",
    "profile_image": "https://example.com/user2.jpg"
  }' | pretty_json
echo -e "\n"


echo "3. 세 번째 사용자 회원가입 (중복)..."
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@test.com",
    "password": "Test1234!",
    "password_confirm": "Test1234!",
    "nickname": "사용자3",
    "profile_image": "https://example.com/user1.jpg"
  }' | pretty_json
echo -e "\n"

echo "4. 네 번째 사용자 회원가입 (이메일 누락)..."
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "password": "Test1234!",
    "password_confirm": "Test1234!",
    "nickname": "사용자3",
    "profile_image": "https://example.com/user1.jpg"
  }' | pretty_json
echo -e "\n"

echo "5. 로그인 테스트 (비밀번호 오류)..."
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@test.com",
    "password": "wrong!"
  }' | pretty_json
echo -e "\n"

echo "6. 로그인 테스트..."
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@test.com",
    "password": "Test1234!"
  }' | pretty_json
echo -e "\n"

echo "5. 게시글 작성..."
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FastAPI로 만든 커뮤니티",
    "content": "안녕하세요! 첫 번째 게시글입니다.",
    "image_url": "https://example.com/post1.jpg",
    "author_id": 1
  }' | pretty_json
echo -e "\n"


echo "6. 두 번째 게시글 작성..."
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "2번째 게시글",
    "content": "FastAPI는 정말 빠르고 좋네요!",
    "author_id": 1
  }' | pretty_json
echo -e "\n"

echo "7. 세 번째 게시글 작성..."
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "3번째 게시글",
    "content": "Python 웹 개발 재미있어요!",
    "author_id": 2
  }' | pretty_json
echo -e "\n"

echo "8. 전체 게시글 조회..."
curl -X GET http://localhost:8000/posts | pretty_json
echo -e "\n"

echo "9. 첫 번째 게시글 상세 조회 (조회수 증가)..."
curl -X GET http://localhost:8000/posts/1 | pretty_json
echo -e "\n"

echo "10. 좋아요 토글..."
curl -X POST "http://localhost:8000/posts/1/like?user_id=1" | pretty_json
echo -e "\n"


echo "11. 댓글 작성..."
curl -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 1,
    "author_id": 2,
    "content": "정말 유익한 글이네요!"
  }' | pretty_json
echo -e "\n"

echo "12. 두 번째 댓글 작성..."
curl -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 1,
    "author_id": 1,
    "content": "감사합니다~"
  }' | pretty_json
echo -e "\n"

echo "13. 게시글의 댓글 목록 조회..."
curl -X GET http://localhost:8000/comments/post/1 | pretty_json
echo -e "\n"

echo "14. 게시글 1 다시 조회 (조회수, 좋아요, 댓글수 확인)..."
curl -X GET http://localhost:8000/posts/1 | pretty_json
echo -e "\n"

echo "15. 회원 1 닉네임 수정..."
curl -X PATCH http://localhost:8000/auth/users/1/nickname \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "수정된1닉네임"
  }' | pretty_json
echo -e "\n"

echo "16. 댓글 1-1 수정..."
curl -X PUT "http://localhost:8000/comments/1?user_id=2" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "수정된 댓글입니다!"
  }' | pretty_json
echo -e "\n"

echo "17. 게시글 1 부분 수정 (제목만)..."
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "수정된 제목"
  }' | pretty_json
echo -e "\n"

echo "18. 좋아요 상태 확인..."
curl -X GET "http://localhost:8000/posts/1/is-liked?user_id=1" | pretty_json
echo -e "\n"

echo "19. 좋아요 토글..."
curl -X DELETE "http://localhost:8000/posts/1/like?user_id=1" | pretty_json
echo -e "\n"

echo "20. 댓글 삭제..."
curl -X DELETE "http://localhost:8000/comments/10?user_id=1" | pretty_json
echo -e "\n"
curl -X DELETE "http://localhost:8000/comments/1?user_id=1" | pretty_json
echo -e "\n"
curl -X DELETE "http://localhost:8000/comments/2?user_id=1" | pretty_json
echo -e "\n"


echo "21. 게시글의 댓글 목록 조회..."
curl -X GET http://localhost:8000/comments/post/1 | pretty_json
echo -e "\n"


echo "22. 전체 게시글 조회..."
curl -X GET http://localhost:8000/posts | pretty_json
echo -e "\n"

echo "23. 첫 번째 게시글 조회..."
curl -X GET http://localhost:8000/posts/1 | pretty_json
echo -e "\n"

echo "24. 게시글 삭제..."
curl -X DELETE "http://localhost:8000/posts/1?user_id=2" | pretty_json
echo -e "\n"
curl -X DELETE "http://localhost:8000/posts/1?user_id=1" | pretty_json
echo -e "\n"
curl -X DELETE "http://localhost:8000/posts/1?user_id=1" | pretty_json
echo -e "\n"

echo "25. 전체 게시글 조회..."
curl -X GET http://localhost:8000/posts | pretty_json
echo -e "\n"

echo "===== 테스트 완료 ====="
