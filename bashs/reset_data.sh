#!/bin/bash

# 한글 깨짐 방지를 위한 함수 정의
pretty_json() {
  python3 -c 'import sys, json; print(json.dumps(json.loads(sys.stdin.read()), indent=2, ensure_ascii=False))'
}

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
