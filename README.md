# Community Backend - FastAPI Learning Project

> FastAPI를 활용한 커뮤니티 백엔드 API 개발 학습 프로젝트

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

[![Postman](https://img.shields.io/badge/Testing-Postman-orange.svg?style=flat&logo=postman&logoColor=white)](https://www.postman.com/)
[![CURL](https://img.shields.io/badge/Testing-CURL-green.svg?style=flat&logo=curl&logoColor=white)](https://curl.se/docs/manpage.html)

추가 예정:
- **Database** | PostgreSQL, SQLAlchemy
- **Authentication** | JWT (JSON Web Token)
- **Security** | bcrypt, CORS, Rate Limiting
- **Validation** | Pydantic v2


[![KakaoTech](https://img.shields.io/badge/kakaotech_bootcamp-ffcd00.svg?logo=kakaotalk&logoColor=000000)](https://kakaotechbootcamp.com/)
[![StartupCode](https://img.shields.io/badge/StartupCode-blue.svg)](https://www.startupcode.kr/)





## Table of Contents

[1. FastAPI 프로젝트 초기 설정 및 HTTP 기초](#1-fastapi-프로젝트-초기-설정-및-http-기초)
- [1-1. 설명](#1-1-설명)
- [1-2. 결과](#1-2-결과)
- [1-3. 문제](#1-3-문제)
- [1-4. 해결](#1-4-해결)

[2. HTTP 메서드 및 요청 처리 - RESTful CRUD 구현](#2-http-메서드-및-요청-처리---restful-crud-구현)
- [2-1. 설명](#2-1-설명)
- [2-2. 결과](#2-2-결과)
- [2-3. 문제와 해결](#2-3-문제와-해결)


---


## 1. FastAPI 프로젝트 초기 설정 및 HTTP 기초

### 1-1. 설명

**branch name:** `feature/init-setup`  
**구현 내용:**
1. `pyproject.toml`: 의존성, 프로젝트 메타데이터 정리 및 이해
2. `main.py`: FastAPI의 기본 구조 작성 - 엔드포인트 이해 및 데코레이터 활용법 학습
3. `main.py`: HTTP Response의 3요소 구현 - Status Code, Headers, Body
4. `main.py`: JSON 직렬화 - Python dict → JSON string, `JSONResponse`
5. `main.py`: Cookie를 통한 상태 관리 - HTTP의 Stateless 문제 및 쿠키 활용 이해

**검증:** Postman으로 `GET` 요청 후  Status Code, Headers, Cookie 확인


### 1-2. 결과
<details>
<summary>직접 테스트해보기</summary>

```sh
uvicorn main:app --reload
```
> - API 문서: http://localhost:8000/docs
> - Health Check: http://localhost:8000/
> - 커스텀 응답: http://localhost:8000/custom
</details>

<details>
<summary>1. <code>GET /</code></summary>

<img src="./data/fig2_pm_root.png" width="500" height="250"/>
</details>
    
<details>
<summary>2. <code>GET /custom</code></summary>

<img src="./data/fig3_pm_custom_status.png" width="500" height="250"/>
</details>



### 1-3. 문제

<details>
<summary>1. Postman에서 Header를 찾을 수 없음.</summary>
<img src="./data/fig4_pm_custom_headers.png" width="500" height="390"/>
</details>
<details>
<summary>2. Postman에서 Cookie setting을 모두 확인할 수 없음.</summary>
<img src="./data/fig5_pm_custom_cookies.png" width="620" height="450"/>
</details>
    


### 1-4. 해결

<details>
<summary>1. `curl` 사용</summary>

- 요청: `curl -v http://localhost:8000/custom`
- 터미널 출력:
    ```zsh
    * Host localhost:8000 was resolved.
    * IPv6: ::1
    * IPv4: 127.0.0.1
    * Trying 127.0.0.1:8000...
    * Connected to localhost (127.0.0.1) port 8000
    > GET /custom HTTP/1.1
    > Host: localhost:8000
    > User-Agent: curl/8.7.1
    > Accept: */*
    > 
    * Request completely sent off
    < HTTP/1.1 200 OK
    < date: Wed, 12 Nov 2025 01:11:25 GMT
    < server: uvicorn
    < kkotech-custom-header: MyValue
    < content-length: 36
    < content-type: application/json
    < set-cookie: session_id=abc123; Path=/; SameSite=lax
    < 
    * Connection #0 to host localhost left intact
    {"status":"success","data":"custom"}%
    ```
</details>
<details>
<summary>2. Developer Tools - Network</summary>

browser ➡️ Developer Tools ➡️ Network
<img src="./data/fig6_browser_network.png" width="650" height="350"/>
</details>






---


## 2. HTTP 메서드 및 요청 처리 - RESTful CRUD 구현

### 2-1. 설명

**branch name:** `feature/http-methods`  
**구현 내용:**  
`main.py` - REST API의 CRUD 연산을 HTTP 메서드에 매핑
1. `Pydantic` 모델 정의 - Request Body 검증(필수/선택) 및 직렬화 (PostCreate, PostPartialUpdate)
2. `POST /posts` - 게시글 생성: 자동 ID 할당, in-memory 저장소
3. `GET /posts`, `GET /posts/{post_id}` - 게시글 조회: Read Collection/Single, Path Parameter
4. `PUT /posts/{post_id}` - 게시글 전체 교체: Idempotent, Update - Full
5. `PATCH /posts/{post_id}` - 게시글 부분 수정: `exclude_unset`
6. `DELETE /posts/{post_id}` - 게시글 삭제: 204 No Content
7. `main.py`: HTTP Status Code 활용 - 200/201/204/404 응답 처리

**검증:** Postman 또는 curl로 5개 HTTP 메서드 테스트
1. create
2. read all
3. read one
4. put
5. patch
6. delete
7. read all
8. read one

---

### 2-2. 결과

<details>
<summary>직접 테스트해보기</summary>

```sh
uvicorn main:app #--reload
```
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/
- 커스텀 응답: http://localhost:8000/custom
- 게시글 목록: http://localhost:8000/posts
```sh
# POST: Create
curl -X POST http://localhost:8000/posts \
-H "Content-Type: application/json" \
-d '{"title":"Test","content":"Hello"}'

# GET: Read all
curl -X PUT http://localhost:8000/posts

# GET: Read one
curl -X PUT http://localhost:8000/posts/1
curl -X GET http://localhost:8000/posts/999

# PUT
curl -X PUT http://localhost:8000/posts/1 \
-H "Content-Type: application/json" \
-d '{"title":"Updated","content":"World"}'

# PATCH
curl -X PATCH http://localhost:8000/posts/1 \
-H "Content-Type: application/json" \
-d '{"title":"Patched"}'

# DELETE
curl -X DELETE http://localhost:8000/posts/1
curl -i -X DELETE http://localhost:8000/posts/999

# GET: Read all
curl -X PUT http://localhost:8000/posts

# GET: Read one
curl -X PUT http://localhost:8000/posts/1
```
</details>

<details>
<summary>1. <code>POST /posts</code> 게시글 생성</summary>

**요청:**
```sh
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"FastAPI 학습","content":"REST API CRUD 구현 완료"}'
```

**응답 (Status 201 Created):**
```json
{
    "message": "Created",
    "data": {
        "id": 1,
        "title": "FastAPI 학습",
        "content": "REST API CRUD 구현 완료"
    }
}
```
</details>


<details>
<summary>2. <code>GET /posts</code> 전체 게시글 조회</summary>

**요청:**
```sh
curl -X GET http://localhost:8000/posts
```

**응답 (Status 200 OK):**
```json
{
    "message": "Success",
    "count": 1,
    "data": [
        {
            "id": 1,
            "title": "FastAPI 학습",
            "content": "REST API CRUD 구현 완료"
        }
    ]
}
```
</details>

<details>
<summary>3. <code>GET /posts/{post_id}</code> 특정 게시글 조회</summary>

**요청:**
```sh
curl -X GET http://localhost:8000/posts/1
curl -X GET http://localhost:8000/posts/999
```

**응답 (Status 200 OK):**
```json
{
    "message": "Success",
    "data": {
        "id": 1,
        "title": "FastAPI 학습",
        "content": "REST API CRUD 구현 완료"
    }
}
```

**존재하지 않는 ID 요청 시 (Status 404 Not Found):**
```json
{
    "error": "Not found",
    "message": "Post with id 999 does not exist"
}
```
</details>

<details>
<summary>4. <code>PUT /posts/{post_id}</code> 게시글 전체 수정</summary>

**요청:**
```sh
curl -X PUT http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"수정된 제목","content":"수정된 내용입니다"}'
```

**응답 (Status 200 OK):**
```json
{
    "message": "Updated",
    "data": {
        "id": 1,
        "title": "수정된 제목",
        "content": "수정된 내용입니다"
    }
}
```
</details>

<details>
<summary>5. <code>PATCH /posts/{post_id}</code> 게시글 부분 수정</summary>

**요청 (제목만 수정):**
```sh
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"부분 수정된 제목"}'
```

**응답 (Status 200 OK):**
```json
{
    "message": "Partially updated",
    "data": {
        "id": 1,
        "title": "부분 수정된 제목",
        "content": "수정된 내용입니다"
    }
}
```
> **Note**: `content` 필드는 이전 값 유지
</details>

<details>
<summary>6. <code>DELETE /posts/{post_id}</code> 게시글 삭제</summary>

**요청:**
```sh
curl -i -X DELETE http://localhost:8000/posts/1
curl -i -X DELETE http://localhost:8000/posts/999
```

**응답 (Status 204 No Content):**
```sh
HTTP/1.1 204 No Content # 응답 본문 없음
date: # 실행한 날짜 출력
server: uvicorn
content-type: application/json
```

**이미 삭제된/없는 ID 요청 시 (Status 404 Not Found):**
```sh
HTTP/1.1 404 Not Found
date: # 실행한 날짜 출력
server: uvicorn
content-length: 65
content-type: application/json
{
  "error": "Not found",
  "message": "Post with id 999 does not exist"
}
```
**이후 Read all (`GET /posts`) 요청 시:**
```json
{
    "message": "Success",
    "count": 0,
    "data": []
}
```

**이후 Read all (`GET /posts/1`) 요청 시:**
```json
{
    "error": "Not found",
    "message": "Post with id 1 does not exist"
}
```
</details>



### 2-3. 문제와 해결

<details>
<summary>1. PATCH 작성 시 None으로 덮어씌워짐</summary>

**문제 상황:**
- `Pydantic BaseModel` & `Optional` 사용으로 `None`값 제외가 보장되는 것으로 착각함
- `PATCH` (부분 수정) 요청 시 전송하지 않은 필드가 `None`으로 덮어씌워지는 문제 발생

- **요청:** `PATCH .../posts/1 {"title":"Patched"}`
- **응답:**
    ```json
    {
        "message": "Partially updated", // failed: content가 None으로 덮어씌워짐.
        "data": {"id":1, "title":"Patched", "content":null}
    }
    ```

**원인:**
```python
@app.patch("/posts/{post_id}")
def partial_update(post_id: int, update_data: PostPartialUpdate) -> JSONResponse:
    # ... 업데이트 로직 ...
    update_dict = update_data.model_dump()
    posts[i].update(update_dict)
    # ... 업데이트 로직 ...
```

**해결: PATCH 구현 시 `exclude_unset` 활용**
```py
update_dict = update_data.model_dump(exclude_unset=True)
```
</details>

<details>
<summary>2. DELETE 시 출력 없음</summary>

**문제 상황:** 삭제 성공 시 JSON 응답을 반환했더니 **응답 본문이 전혀 표시되지 않음**

**원인:**
```python
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    # ... 삭제 로직 ...
    return JSONResponse(status_code=204,
            content={"message": f"Post with id {post_id} deleted"})
```

**해결: 삭제 성공 시 `return None` (또는 빈 반환)**
```py
return None
```
- HTTP 표준에 따르면 DELETE 엔드포인트 204 No Content는 본문이 없어야 함
- FastAPI가 자동으로 204 No Content 처리
- 이때 OpenAPI 자동 문서화를 명확히 하려면 `status_code=204`를 데코레이터로 명시해야 함

</details>


## 다음 단계

- [ ] 데이터베이스 연동 (SQLAlchemy + PostgreSQL)
- [ ] 인증/인가 (JWT Token)
- [ ] 페이지네이션 구현
- [ ] 에러 핸들링 미들웨어
- [ ] 유닛 테스트 작성 (pytest)
- [ ] Docker 컨테이너화