"""
테스트 사용자 생성 스크립트
"""
from app.databases import SessionLocal
from app.models.user_model import UserModel
from app.utils.auth import hash_password

# 데이터베이스 세션 생성
db = SessionLocal()

try:
    user_model = UserModel(db)

    # 테스트 사용자 생성
    test_user = user_model.create(
        email="testuser@test.com",
        password=hash_password("Test1234!"),
        nickname="testuser"
    )

    print(f"✅ 테스트 사용자 생성 완료!")
    print(f"   - ID: {test_user.id}")
    print(f"   - Email: {test_user.email}")
    print(f"   - Nickname: {test_user.nickname}")
    print(f"   - Password: Test1234!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    db.rollback()

finally:
    db.close()
