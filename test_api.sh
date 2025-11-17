#!/bin/bash

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
  }' | python3 -m json.tool
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
  }' | python3 -m json.tool
echo -e "\n"

echo "3. 로그인 테스트..."
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@test.com",
    "password": "Test1234!"
  }' | python3 -m json.tool
echo -e "\n"

echo "4. 게시글 작성..."
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FastAPI로 만든 커뮤니티",
    "content": "안녕하세요! 첫 번째 게시글입니다.",
    "image_url": "https://example.com/post1.jpg",
    "author_id": 1
  }' | python3 -m json.tool
echo -e "\n"

echo "5. 두 번째 게시글 작성..."
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python 웹 개발",
    "content": "FastAPI는 정말 빠르고 좋네요!",
    "author_id": 2
  }' | python3 -m json.tool
echo -e "\n"

echo "6. 전체 게시글 조회..."
curl -X GET http://localhost:8000/posts | python3 -m json.tool
echo -e "\n"

echo "7. 첫 번째 게시글 상세 조회 (조회수 증가)..."
curl -X GET http://localhost:8000/posts/1 | python3 -m json.tool
echo -e "\n"

echo "8. 좋아요 추가..."
curl -X POST "http://localhost:8000/posts/1/like?user_id=1" | python3 -m json.tool
echo -e "\n"

echo "9. 댓글 작성..."
curl -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 1,
    "author_id": 2,
    "content": "정말 유익한 글이네요!"
  }' | python3 -m json.tool
echo -e "\n"

echo "10. 두 번째 댓글 작성..."
curl -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 1,
    "author_id": 1,
    "content": "감사합니다~"
  }' | python3 -m json.tool
echo -e "\n"

echo "11. 게시글의 댓글 목록 조회..."
curl -X GET http://localhost:8000/comments/post/1 | python3 -m json.tool
echo -e "\n"

echo "12. 게시글 다시 조회 (조회수, 좋아요, 댓글수 확인)..."
curl -X GET http://localhost:8000/posts/1 | python3 -m json.tool
echo -e "\n"

echo "13. 닉네임 수정..."
curl -X PATCH http://localhost:8000/auth/users/1/nickname \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "수정된닉네임"
  }' | python3 -m json.tool
echo -e "\n"

echo "14. 댓글 수정..."
curl -X PUT "http://localhost:8000/comments/1?user_id=2" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "수정된 댓글입니다!"
  }' | python3 -m json.tool
echo -e "\n"

echo "15. 게시글 부분 수정 (제목만)..."
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "수정된 제목"
  }' | python3 -m json.tool
echo -e "\n"

echo "16. 좋아요 상태 확인..."
curl -X GET "http://localhost:8000/posts/1/is-liked?user_id=1" | python3 -m json.tool
echo -e "\n"

echo "===== 테스트 완료 ====="
