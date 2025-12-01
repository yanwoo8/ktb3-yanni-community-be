# clone
# git clone https://github.com/yanwoo8/ktb3-yanni-community-be.git
# cd ktb3-yanni-community-be



# ==================== Community Backend Setup Script ====================
#
# 로컬 환경 자동 세팅 스크립트
#
# 1. Python 가상환경 생성
# 2. 의존성 패키지 설치
# 3. 환경변수 설정 (.env 파일 생성)
# 4. 데이터베이스 초기화
# 5. 개발 서버 실행 안내
#
# 사용법:
#   chmod +x setup.sh
#   ./setup.sh
#
# ========================================================================

set -e  # 에러 발생 시 스크립트 중단

echo "=========================================="
echo "Community Backend Setup Script"
echo "=========================================="
echo ""

CONDA_ENV_NAME="web"


# ==================== 1. Python 버전 확인 ====================

echo "[1/6] Python 버전 확인 중..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo "Python 3.10 이상을 설치해주세요: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.10 이상이 필요합니다. 현재 버전: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python 버전: $(python3 --version)"
echo ""

# ==================== 2. 가상환경 선택 및 설정 ====================

echo "[2/6] Python 가상환경 설정 중..."

# Conda 환경 확인
if command -v conda &> /dev/null; then
    echo "🔍 Conda가 설치되어 있습니다."
    echo ""
    echo "어떤 가상환경을 사용하시겠습니까?"
    echo "  1) Conda 환경"
    echo "  2) venv (Python 기본 가상환경)"
    read -p "선택 (1 또는 2, 기본값: 1): " ENV_CHOICE
    ENV_CHOICE=${ENV_CHOICE:-1}
    echo ""

    if [ "$ENV_CHOICE" = "1" ]; then
        # Conda 환경 사용

        # 기존 환경 확인
        if conda env list | grep -q "^$CONDA_ENV_NAME "; then
            echo "⚠️  기존 Conda 환경 '$CONDA_ENV_NAME'이 존재합니다."
            read -p "기존 환경을 사용하시겠습니까? (Y/n): " -n 1 -r
            echo

            if [[ $REPLY =~ ^[Nn]$ ]]; then
                echo "🗑️  기존 환경을 제거합니다..."
                conda env remove -n $CONDA_ENV_NAME -y > /dev/null 2>&1
                #------------------------------------------------------
                echo "📦 새로운 Conda 환경을 생성합니다..."
                conda create -n $CONDA_ENV_NAME python=3.10 -y > /dev/null 2>&1
                #------------------------------------------------------
                echo "✅ Conda 환경 '$CONDA_ENV_NAME' 생성 완료"
            else
                echo "✅ 기존 Conda 환경 '$CONDA_ENV_NAME'을 사용합니다."
            fi

        else
            echo "📦 Conda 환경 '$CONDA_ENV_NAME'을 생성합니다..."
            conda create -n $CONDA_ENV_NAME python=3.10 -y > /dev/null 2>&1
            #------------------------------------------------------
            echo "✅ Conda 환경 '$CONDA_ENV_NAME' 생성 완료"
        fi

        # Conda 환경 활성화
        echo "🔄 Conda 환경을 활성화합니다..."
        eval "$(conda shell.bash hook)"
        conda activate $CONDA_ENV_NAME
        echo "✅ Conda 환경 '$CONDA_ENV_NAME' 활성화 완료"

        USE_CONDA=true

    else
        # venv 사용
        if [ -d "venv" ]; then
            echo "⚠️  기존 venv 가상환경이 존재합니다. 재사용합니다."
        else
            echo "📦 venv 가상환경을 생성합니다..."
            python3 -m venv venv
            echo "✅ venv 가상환경 생성 완료"
        fi

        # venv 활성화
        source venv/bin/activate
        echo "✅ venv 가상환경 활성화 완료"

        USE_CONDA=false
    fi

else
    # Conda가 없으면 venv 사용
    echo "📦 venv 가상환경을 설정합니다..."

    if [ -d "venv" ]; then
        echo "⚠️  기존 venv 가상환경이 존재합니다. 재사용합니다."
    else
        python3 -m venv venv
        echo "✅ venv 가상환경 생성 완료"
    fi

    # venv 활성화
    source venv/bin/activate
    echo "✅ venv 가상환경 활성화 완료"

    USE_CONDA=false
fi

echo ""

# ==================== 3. 의존성 패키지 설치 ====================

echo "[3/6] 의존성 패키지 설치 중..."

pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip 업그레이드 완료"

pip install -e . > /dev/null 2>&1
echo "✅ 프로젝트 의존성 설치 완료 (httpx, FastAPI, SQLAlchemy 등)"

echo ""

# ==================== 4. 환경변수 설정 ====================

echo "[4/6] 환경변수 설정 중..."

if [ -f ".env" ]; then
    echo "⚠️  .env 파일이 이미 존재합니다. 건너뜁니다."
else
    cat > .env << 'EOF'

# ==================== Community Backend 환경변수 ====================

# OpenRouter API Key (AI 댓글 생성용)
# 발급 방법: https://openrouter.ai/keys
# 무료 모델 사용: google/gemini-2.0-flash-exp:free
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Database (SQLite - 기본값)
# 파일 경로: ./community.db
DATABASE_URL=sqlite:///./community.db

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True

# Logging
LOG_LEVEL=INFO

# ========================================================================
EOF
    echo "✅ .env 파일 생성 완료"
    echo ""
    echo "⚠️  중요: .env 파일을 열고 다음 값을 설정해주세요:"
    echo "   - OPENROUTER_API_KEY: OpenRouter API 키"
    echo "     발급 링크: https://openrouter.ai/keys"
    echo ""
fi

echo ""

# ==================== 5. 데이터베이스 초기화 ====================

echo "[5/6] 데이터베이스 초기화 중..."

if [ -f "community.db" ]; then
    echo "⚠️  기존 데이터베이스가 존재합니다."
    read -p "데이터베이스를 초기화하시겠습니까? (y/N): " -n 1 -r

    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm community.db
        echo "✅ 기존 데이터베이스 삭제 완료"
    else
        echo "⏭️  데이터베이스 초기화를 건너뜁니다."
    fi
fi

echo "✅ 데이터베이스는 서버 시작 시 자동으로 초기화됩니다."
echo ""

# ==================== 6. 설정 완료 ====================

echo "[6/6] 설정 완료!"
echo ""
echo "=========================================="
echo "✅ 모든 설정이 완료되었습니다!"
echo "=========================================="
echo ""
echo "📋 다음 단계:"
echo ""
echo "1. 환경변수 설정 (필수!)"
echo "   .env 파일을 열고 OPENROUTER_API_KEY를 설정하세요."
echo "   발급 링크: https://openrouter.ai/keys"
echo ""
echo "2. 개발 서버 실행"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. API 문서 확인"
echo "   http://localhost:8000/docs"
echo ""

if [ "$USE_CONDA" = true ]; then
    echo "   - Conda 환경 활성화: conda activate web"
    echo "   - Conda 환경 비활성화: conda deactivate"
else
    echo "   - venv 환경 활성화: source venv/bin/activate"
    echo "   - venv 환경 비활성화: deactivate"
fi

echo ""
echo "🔗 추가 정보:"
echo "   - GitHub: https://github.com/yanwoo8/ktb3-yanni-community-be"
echo "   - OpenRouter 문서: https://openrouter.ai/docs"
echo ""



# =====================================================

# run server
uvicorn main:app --reload