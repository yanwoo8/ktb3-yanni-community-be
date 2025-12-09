> ❓: 더 공부해보고 추가할 것들


# Table of Contents
1. [Basic](#basic)
2. [HTTP](#http)
3. [URL and Endpoint](#url-and-endpoint)
4. [Architecture](#architecture)
5. [DB](#db)
6. [Security](#security)
7. [FastAPI and Server Development](#fastapi-and-server-development)
8. [Session and Cookie](#session-and-cookie)
9. [Advanced Features](#advanced-features)
10. [Model Serving](#model-serving)



## Basic

- **Client 클라이언트**: 고객-요청자. Request-er
- **Server 서버**: 응대자-답변자. Response-r
- `pyproject.toml`: 파이썬 프로젝트의 설정과 메타데이터를 적어놓는 구성파일
- **메타데이터**: 데이터에 대한 데이터. 실제 내용(데이터)이 아니라, 그 데이터를 설명하는 정보.<br>
    ex) 데이터: "안녕하세요" - 메타데이터: "이 데이터의 언어는 한국어다."


- **Create 생성**: 메모리/디스크에 실체가 만들어짐 (파일, 객체 등)
- **Define 정의**: 코드로 "이런 것이 있다"고 선언

```py
# 정의 (Definition)
@app.get("/users")  # "GET /users 경로는 이 함수를 실행한다"고 정의
def get_users():
    return []

# 생성 (Creation)
user = User(name="Alice")  # 메모리에 User 객체 생성
```







<br>
<br>








## HTTP

- **HTTP**: Hyper-Text Transfer Protocol. 하이퍼텍스트(일반적인 텍스트를 뛰어넘는 기능이 있는 구조화된 텍스트)를 전송하는 (통신)규약.

- **HTTP Message 메시지**: 클라이언트-서버 간 통신 기본 단위.
    - Request / Response
    - 시작줄(start line): `{Method} {dir} {HTTP version}`
    - 헤더(HTTP headers): Request / General / Representation
    - 빈 줄(empty line): 헤더와 본문 구분
    - 본문(body): JSON 데이터나 HTML 문서 등 실제 내용
    

- **Query string / Query Parameter / 쿼리 매개변수**: (웹페이지-클라이언트-에 대한) 추가 정보 전달 - `GET /posts?offset=0&limit=10`
- **Path Variable / Path Parameter / 경로 매개변수**: 특정한 경로에 있는 특정 자원을 식별하는 변수 - `GET /posts/1`


- **HTTP Request Method 요청 메서드**: HTTP 요청 방법. 서버에게 어떤 작업을 수행하길 원하는지 알리는 방법.
    - **GET**: 데이터 조회 요청 (QS: 검색, 필터링, 정렬 등의 추가적 정보 / PV: 특정 위치의 데이터 요청)
    - **POST**: 데이터 생성, 업데이트 요청 (QS: _ / PV: _ )
    - **PUT**: 데이터 대체 / 전체 업데이트 (Replace) 요청 - 프로필 이미지 변경 등 (QS: _ / PV: _ )
    - **PATCH**: 데이터 부분 업데이트 (Partial Update) 요청 - 비밀번호 변경 등 (QS: _ / PV: `PATCH /users/1`은 사용자 ID가 1인 사용자 정보의 일부 내용을 수정하는 PATCH 요청)
    - **DELETE**: 데이터 삭제 요청 (QS: _ / PV: `DELETE /users/1`은 사용자 ID가 1인 사용자 정보를 삭제하는 DELETE 요청)


- **HTTP Status Code 상태 코드**: HTTP 진행 상태 플래그(표시 코드)
    - 1xx: 정보
    - 2xx: 성공
    - 3xx: 리다이렉션
    - 4xx: 클라이언트 오류
    - 5xx: 서버 오류

- **HTTP URL**: Scheme + Domain + Port + Resource path + Parameters(QS & PV)







<br>
<br>






## URL and Endpoint

```py
@app.get("/users")  # ← 이 순간 URL "/users"를 정의
def get_users():    # 동시에 엔드포인트 "(GET /users) -> get_users()" 정의
    return []
```

1. 클라이언트: GET /users 요청 <- HTTP Request Message
2. FastAPI: routing_table에서 ("GET", "/users") 검색 <- Routing
3. FastAPI: 해당하는 함수(get_users) 발견
4. FastAPI: get_users() 함수 실행
5. FastAPI: 결과를 HTTP 응답으로 변환하여 전송 <- Response


- **URL (Uniform Resource Locator): 정해진 자원 주소/위치.**
    - 프로그래머가 코드로 정의한 논리적 주소.
    - 정의하지 않으면 404 Error 발생.
    - 엔드포인트를 정의할 때 URL이 "정의"된다. "생성"이 아님. 프로그래머가 임의로 정의한다.
    - 기존에 다른 방법으로 생성된 것이 아니라, 프로그래머가 코드로 정의하는 순간 그 경로가 의미를 갖는다.


- **Endpoint 엔드포인트: 서버에 정의된 기능의 주소.**
    - End + Point = 통신의 끝 지점. 클라이언트가 요청을 보낼 때, 그 요청이 도달하는 최종 지점이라는 의미.
    - **형태**: 서버에서 클라이언트가 요청을 보낼 주소 (URL 경로) + 그 주소를 처리하는 코드 (HTTP 메서드)의 조합.
    - 엔드포인트는 "주소+메서드 조합"이며, 이것이 핸들러 함수로 매핑된다.
    - **핸들러 함수**: 실행될 코드
    - 서버 개발자가 정의하며, 서버 실행 시 라우팅 테이블 내에 고정된다.
    - 코드에 명시적으로 작성해야 정의되며, 정의하지 않으면 존재하지 않음.
    - 정의하지 않으면 405 Error 발생.
    - 엔드포인트는 Request(요청)을 받아 처리(handler)하고 Response(status-code, header, body)을 반환함.
    - 라우팅 테이블에 딕셔너리 (해시 테이블) 형태로 저장된다.
    - `(HTTP METHOD, URL): method_url_function()` 형태로 매핑된 해시 테이블의 한 요소.
    - 라우터 테이블의 **키(HTTP METHOD, URL)**만 뜻하는 것인지, **함수(function method)**까지 포함한 의미인지는 맥락에 따라 다르며 둘다 가능함.
    - `@app.get("/")` -> 루트 엔드포인트: `GET /`, URL `/` 정의됨.


|   맥락   |       의미      |            예시             |
|---------|----------------|----------------------------|
| API 문서 | 키만 (메서드+URL) | "GET /users 엔드포인트 제공"   |
| 개발 대화 | 전체 (키+함수)    | "users 엔드포인트 수정함"       |
| 기술 논의 | 키만            | "이 엔드포인트에 매핑된 함수는..." |



- **Routing 라우팅: 어떤 함수를 실행할지 결정하는 과정**
    - Request 요청(HTTP Method + URL)이 들어왔을 때, 이 요청을 키로 삼아 라우팅 테이블에서 매핑된 핸들러 함수를 찾아 호출한다.
    - 라우팅 테이블은 서버 실행 시 메모리에 생성됨
    1. **요청(키) 분석**: `GET /users` 분해
    2. **테이블 조회**: 해당하는 함수 찾기
    3. **함수 실행**: 찾은 함수 호출
    4. **응답 반환**: 결과를 HTTP 응답으로 변환

```py
# FastAPI 내부에서 이렇게 저장 (단순화한 개념)
routing_table = {
    ("GET", "/users"): get_users,           # 함수 참조
    ("POST", "/users"): create_user,        # 함수 참조
    ("GET", "/posts/{post_id}"): get_post,  # 함수 참조
}
```

```
[RAM]
├── FastAPI 프로세스
│   ├── 라우팅 테이블 (딕셔너리 형태)
│   │   ├── Key: ("HTTP메서드", "URL패턴")
│   │   └── Value: 함수 객체의 메모리 주소
│   ├── 함수 코드 (바이트코드)
│   └── 기타 서버 데이터
```

- **Dynamic Routing Protocol 동적 경로 처리**:
    - Endpoint 정의 시 URL의 일부를 변수로 받아 처리하도록 작성하는 것.
    - `@app.get("/users/{user_id}")`

`from fastapi import APIRouter`:
- 라우트 그룹화: 관련된 엔드포인트들을 하나의 모듈로 묶음
- 공통 설정 적용: 모든 엔드포인트에 /posts prefix 자동 추가
- API 문서화: tags=["posts"]로 Swagger UI에서 그룹화
- 모듈화: main.py에서 app.include_router(router)로 등록
- 사용법: route file에서 글로벌로 한 번만 생성하고 이후 모든 엔드포인트에서 재사용. 동일한 router 인스턴스에 여러 엔드포인트를 등록할 수 있음


### Endpoint vs. HTTP message

|   -   |        Endpoint       |         HTTP message        |
|-------|-----------------------|-----------------------------|
| Where |        서버 코드        | 클라이언트 - 서버 간 네트워크 통신  |
| What  | 정의된 기능의 주소        | 실제 통신 데이터                 |
| Role  | 기능 정의 및 매핑         | 데이터 전송                    |
| Who   | 서버 개발자가 정의        | 클라이언트가 전송                 |
| When  | 서버 실행 시 고정됨 (호출) | 클라이언트가 요청할 때마다 새로 생성됨 |
| 비유   | 식당 메뉴판의 항목        | 손님이 주문한 주문서              |
| EX    | `@app.get("/")`      | `GET /`                      |







<br>
<br>






## Architecture


- **Business Logic 비즈니스 로직**: 실제 문제를 해결하는 핵심 규칙과 처리 (코드)
    - 도메인 규칙 (게임 규칙, 은행 규칙 등)
    - 핵심 계산 (추천 알고리즘, 요금 계산 등)
    - 업무 흐름 (주문 → 결제 → 배송 등)

    **≠ 기술 코드** (HTTP, 파싱, DB 연결 등)
    - **비즈니스로직과 기술코드의 차이** : 이 코드를 다른 도메인/회사/서비스에서 가져다가 쓸 수 있나?
        - Yes: 기술 코드
        - No: 비즈니스 로직

    ```
    HTTP 통신 <- 기술 코드
    JSON 파싱 <- 기술 코드
    --- 비즈니스 로직 시작 ---
    만약 A 이면 B를 반환한다.
    만약 C 이면 C += D 한다.
    핵심적인 계산 로직
    --- 비즈니스 로직 끝 ---
    JSON 반환 <- 기술 코드
    HTTP 응답 <- 기술 코드
    ```


**Routes - Controller - Model 구조**: 3계층 분리 (한 파일에 다 쓰지 말고, 역할별로 분리하자)
```
[클라이언트]
     ↓ HTTP 요청
[Route] ← "GET /users로 요청이 왔네"
     ↓ 함수 호출
[Controller] ← "사용자 목록 가져오는 로직 실행"
     ↓ 데이터 요청
[Model] ← "데이터베이스에서 User 데이터 가져오기"
     ↓ 데이터 반환
[Database]
```
- Route가 Controller에 의존한다. (Route → Model)
- Controller가 Model에 의존한다. (Model → Controller)


- **Route: HTTP 요청/응답 처리 (엔드포인트 정의 및 함수 호출)**
    - URL 경로 정의
    - HTTP 메서드 지정 (GET, POST 등)
    - Controller 함수 호출
    - 비즈니스 로직 없음! (단순 연결만)
    - **식당 예시: 웨이터 (주문을 받고, 음식을 서빙)**

- **Controller: 비즈니스 로직 수행**
    - 비즈니스 로직 실행 (핵심!)
    - 데이터 검증 (나이, 이름 등) & 예외 처리
    - Model 호출하여 데이터 가져오기
    - **식당 예시: 셰프 (요리)**

- **Model: 데이터베이스 접근**
    - 데이터 구조 정의 (Pydantic 모델)
    - 데이터베이스 CRUD (Create, Read, Update, Delete)
    - 비즈니스 로직 없음! (단순 데이터 접근만)
    - **식당 예시: 창고 관리자 (재료 가져오기)**


- **Dependency Injection 의존성 주입**: 객체가 필요한 의존성을 외부에서 주입받음
    - A가 동작하기 위해 B가 필요할 때, A는 B에 의존한다
    - fastapi: `Depends()` 함수를 통해 의존성을 선언
    - `Afunction(param = Depends(Bfunction))` == A는 B를 필요로 한다.
    - 이러면 fastapi가 알아서 B를 먼저 수행할 수 있도록 보장해줌

    - 장점1. 결합도 낮춤
    - 장점2. 테스트 용이 (Mock 주입 가능)
    - 장점3. 코드 재사용성 향상




- **SOC (Separation of Concerns, 관심사의 분리)**: 프로그램을 서로 다른 관심사(책임)에 따라 구분된 섹션으로 나누는 설계 원칙
    - 각 섹션이 특정 관심사만 다루도록 분리
    - 코드의 복잡도 감소, 유지보수성 향상

    * routes: HTTP 요청/응답 처리
    * controllers/services: 비즈니스 로직
    * schemas/models: 데이터 구조
    * models/repositories: 데이터베이스 접근


**SOLID 원칙**
* S - SRP: 클래스는 하나의 책임만
* O - Open/Closed Principle: 확장에는 열려있고, 수정에는 닫혀있음
* L - Liskov Substitution Principle: 자식 클래스는 부모 클래스를 대체 가능해야 함
* I - Interface Segregation Principle: 클라이언트가 사용하지 않는 메서드에 의존하면 안 됨
* D - DIP: 추상화에 의존, 구체화에 의존 X

- **SRP (Single Responsibility Principle, 단일 책임 원칙)**: 클래스나 모듈은 하나의 책임만 가져야 하며, 변경할 이유도 단 하나여야 함.
    - 한 가지 이유로만 변경되도록 설계
    - 높은 응집도, 낮은 결합도

- **의존성 역전 원칙(DIP/Dependency Inversion Principle)**: 역방향 의존 없음
    - 상위 모듈은 하위 모듈에 의존하면 안 됨
    - 모든 모듈은 **추상화(인터페이스)**에 의존해야 함
    - **구체적인 것이 추상적인 것에 의존**해야 함

    - 테스트 용이성 향상
    - 유연한 코드 변경





- **계층화 아키텍처 (Layered Architecture)**: 시스템을 수평적 계층으로 나누어, 각 계층이 특정 책임만 담당
    1. Presentation Layer: TTP 요청/응답, UI
    2. Business Logic Layer: 비즈니스 규칙, 로직
    3. Data Access Layer: 데이터베이스 접근
    4. Database Layer: 실제 데이터 저장소

    * 각 계층은 바로 아래 계층만 호출 가능 (예: 1번에서 2번 호출)
    * 위 계층은 아래 계층에 의존하지만, 역은 불가능

    - 장점: 이해하기 쉽고, 유지보수 편함
    - 단점: 계층 간 강한 결합, 비즈니스 로직이 프레임워크에 의존

- **MVC 패턴 (Model-View-Controller)**: 애플리케이션을 3가지 역할로 분리
    - Model: 데이터와 비즈니스 로직
    - View: 사용자에게 보여지는 부분 (HTML, JSON)
    - Controller: 입력을 받아 Model과 View를 조율
    ```
    User Input
        ↓
    Controller → Model
        ↓         ↓
           View
            ↓
        Response
    ```
    * 장점: 역할 분리 명확
    * 단점: View-Controller가 강하게 결합될 수 있음

- **Domain-Driven Design (DDD)**: 복잡한 비즈니스 도메인을 중심으로 설계. 비즈니스 로직이 핵심
    - Entity (엔티티): 고유 식별자를 가진 객체
    - Value Object (값 객체): 식별자 없이 값으로만 구분
    - Aggregate (집합체): 여러 Entity와 Value Object의 묶음
    - Repository (저장소): Aggregate를 저장/조회
    - Domain Service (도메인 서비스): Entity에 속하지 않는 비즈니스 로직

    * 장점: 복잡한 비즈니스 로직 관리에 최적
    * 단점: 학습 곡선 높음, 작은 프로젝트에는 과함


- **Event-Driven Architecture**: 이벤트를 중심으로 시스템 간 통신 (비동기)
    
    장점:
    - 느슨한 결합
    - 확장성 (새 리스너 추가 쉬움)
    - 비동기 처리 (성능 향상)
    
    단점:
    - 복잡도 증가
    - 디버깅 어려움
    - 데이터 일관성 문제 (Eventual Consistency)




- ❓Model Config
- ❓Model Inheritance

- ❓**Clean Architecture**: 비즈니스 로직을 외부 의존성으로부터 독립시키는 아키텍처
- ❓Service Layer Pattern
- ❓Repository 패턴 (데이터 접근 추상화): 데이터 접근 로직을 추상화하여 컬렉션처럼 다룸






<br>
<br>






## DB

- **DB (Database 데이터베이스)**: 자료를 정보로써 활용하기 위해 구조화해놓은 데이터 모음.
- **RDB (RelationalDB 관계형 데이터베이스)**: 자료를 정보로 활용하기 위해서 테이블 형태로 관계를 맺어 놓은 데이터 모음
- **SQL (Structured Query Language)**: DB 시스템에서 자료를 처리하기 위해 사용하는 구조화된 쿼리 언어
- **DDL 데이터 정의어**: DB 구조 변경 - 데이터베이스 생성, 테이블 추가/수정/삭제
- **DML 데이터 조작어**: 데이터 조회/추가/수정/삭제/정렬/그룹/...
- **DCL 데이터 제어어**: 사용자에게 권한 부여/취소
- `JOIN`/`VIEW`/`UNION`

- ❓SQLite
- ❓ORM이란? (Object-Relational Mapping)
- ❓SQLAlchemy 기초
- ❓관계(Relationship) 이해 (1:N, N:M)


- **Transaction 트랜잭션: "하나의 논리적 작업 단위"로 묶인 여러 데이터베이스 작업들**
    - 하나라도 누락되면 전체가 실패하는 것과 마찬가지인 작업 뭉탱이가 있음. (예: 돈 보내기 - 돈받기)
    - 이러한 작업들을 하나의 트랜잭션으로 묶음
    - 둘 다 성공 → commit (확정)
    - 하나라도 실패 → rollback (전체 취소)

- **ACID 속성: Transaction 트랜잭션의 4가지 보장 사항**
- **Atomicity (원자성)**: 전부 성공 or 전부 실패
- **Consistency (일관성)**: 데이터 무결성 유지
- **Isolation (격리성)**: 동시 실행 트랜잭션은 서로 영향 없음
- **Durability (지속성)**: commit 후엔 영구 저장


- **Unit of Work 패턴**: 여러 Model/Repository 작업(데이터베이스 작업)을 하나의 트랜잭션으로 묶음


- **Session 세션: 애플리케이션과 데이터베이스 사이의 통신 관리 중개자 / 대화 창구**  
    웹 세션(vs. 쿠키)이랑 다른 개념임!! 오해 금지.

    **애플리케이션 - 세션(중개자) - 데이터베이스**
    * 애플리케이션은 DB에 직접 접근 불가
    * 세션(중개자)이 애플리케이션 요청 처리 - DB 접근 및 조작
    * 상태 (트랜잭션의 변경사항) 추적
    * 격리성: 세션은 하나의 요청만 처리

    0. **저장 내용:**
        - 실행 중인 SQL 쿼리
        - 트랜잭션 상태 (commit 전 변경사항)
        - DB 연결 정보
    1. **쿼리 빌더 제공:** `db.query()`
    1. **트랜잭션 관리:**
        - 변경사항을 메모리에 기록 (`db.add()`) : 대기열(pending)에 추가
        - 실제로 DB에 저장 (`db.commit()`) :
            1. 대기열의 모든 변경사항을 SQL로 변환
            2. SQL을 데이터베이스로 전송
        - 오류 시 취소 (롤백) (`db.rollback()`)
    2. **쿼리 실행:** 데이터베이스 조작
    3. **객체 추적:**
        - ORM 객체의 변경을 자동 감지
        - `commit()` 시 자동으로 UPDATE 쿼리 생성
    4. **DB 연결 관리:** `db.close()`
    
    - 각 HTTP 요청마다 새 세션 생성
    - 요청 완료 후 자동 종료 (메모리 누수 방지)
    - 백그라운드 작업은 독립적인 세션 필요


| 항목     | 데이터베이스 세션        | 웹 세션 (쿠키/세션)               |
|---------|----------------------|-------------------------------|
| 목적     | DB와의 통신 관리        | 사용자 상태 유지                  |
| 수명     | HTTP 요청 동안만 (짧음) | 로그인 유지 기간 (길음)            |
| 저장 위치 | 서버 메모리            | 서버 메모리 + 쿠키(클라이언트)       |
| 저장 내용 | SQL 쿼리, 트랜잭션 상태  | 사용자 ID, 장바구니, 설정 등        |
| 관계     | 1 요청 = 1 세션        | 1 사용자 = 1 세션 (여러 요청에 걸쳐) |


- **ORM:Object-Relational Mapping: 객체와 데이터베이스 테이블을 자동으로 연결해주는 기술**  
    **Python 코드에서 SQL 쿼리를 쓰는 방법:**

    | 방식 | Non-ORM 방식 | ORM 방식 |
    | 방법 | SQL 직접 작성 | `데이터베이스.query(ORM 클래스 타입).쿼리내용` |
    | 행(row) | 딕셔너리/튜플로 반환 | Python 클래스의 인스턴스(객체)처럼 활용 |
    | column | column name이 명확하지 않아서 혼란 | 속성명=column name (명확함) |
    | 타입안정성 | 없음 - 타입체크 불가 | 있음 - 잘못된 속성 접근 시 즉시 에러 발생 |
    | 오타 방지 | 불가 - 실행 전까지는 오류 x | 가능 - 잘못된 속성 접근 시 즉시 에러 발생 |
    | IDE 자동 완성 | 없음 | 있음 (클래스의 속성명) |

    **사용방식:**
    1. ORM 모델 정의: columns, relationship 정의
    2. ORM 모델이 자동 처리:
        - 데이터 접근
        - JSON 쿼리 자동 실행
        - 다대다 관계 자동 조회
        - 데이터 수 자동 계산
        - ...등등
    3. HTTP 요청 하나당 세션 1개 생성
    
    **장점:**
    1. 생산성: SQL 작성 시간 단축
    2. 타입 안전성: IDE 지원으로 오류 사전 방지
    3. 유지보수성: Python 코드로 DB 구조 관리
    4. 데이터베이스 독립성: SQLite → PostgreSQL 전환 시 코드 변경 최소화
    5. 관계 처리: JOIN 쿼리 자동 생성
    
    **단점:**
    1. 학습 곡선: 새로운 API 학습 필요
    2. 성능: 복잡한 쿼리는 직접 SQL이 더 빠를 수 있음
    3. 추상화: 내부 동작을 모르면 디버깅 어려움


- **관계(Relationship): 테이블 간의 연결 규칙**
    ```py
    liked_by_users = relationship(
        "User",                  # 연결할 클래스 (모델)
        secondary=post_likes,    # 중간 테이블
        back_populates="liked_posts"
    )

    class User(Base):
        # ...
        liked_posts = relationship(
            "Post",
            secondary=post_likes,
            back_populates="liked_by_users"
        )
    ```

    - **1:N** 하나의 A가 여러 개의 B를 가질 수 있음
        - 한 명의 사용자는 여러 개의 게시글을 작성할 수 있음
        - 하나의 게시글은 한 명의 사용자만 작성할 수 있음

    - **N:M** 여러 A가 여러 B를 가질 수 있음
        - 한 명의 사용자는 여러 게시글에 좋아요를 누를 수 있음
        - 하나의 게시글은 여러 사용자로부터 좋아요를 받을 수 있음

    - `back_populates=` : 양방향 관계 설정
    - `secondary=` : 중간 테이블 지정 (N:M만 사용)
    - `cascade="all, delete-orphan"` : 부모 삭제 시 자식도 삭제



- **데이터베이스 엔진 (Database Engine): 데이터를 저장하고 조회하는 핵심 소프트웨어**
    - SQL 쿼리 해석 및 실행
    - 데이터를 디스크에 읽기/쓰기
    - 트랜잭션 관리 (ACID 보장)
    - 인덱스 관리
    - 동시성 제어 (여러 사용자 동시 접근)

    * SQLite (파일 기반)
    * PostgreSQL (서버 기반)
    * MySQL (서버 기반)
    * MongoDB (NoSQL)

        
    - **SQLite: 파일 기반의 경량 관계형 임베디드 데이터베이스 엔진**
        - **임베디드 데이터베이스**: 애플리케이션에 직접 내장되어 서버 없이 동작 가능한 데이터베이스
        - 라이브러리처럼 애플리케이스에 포함
        - 설치/설정 불필요 (serverless)
        - 작은 용량, 빠른 속도
        - 개발/테스트 환경에 적합
        - 동시 쓰기 제한 (읽기는 동시 가능)
        ```
        일반 DB (PostgreSQL, MySQL):
        App → Network → DB Server → Disk

        임베디드 DB (SQLite):
        App → SQLite Library → Disk (직접 접근)
        ```

- **ORM (Object-Relational Mapping) 라이브러리**

    - **SQLAlchemy: ORM 라이브러리**
        - Python 객체 ↔ 데이터베이스 테이블을 매핑
        - Python 클래스로 테이블 정의
        - 다양한 데이터베이스(SQLite, PostgreSQL, MySQL 등)를 지원하는 추상화 계층
        - 데이터베이스 독립적 (DB 변경 시 코드 수정 최소화)
        - SQL을 Python 코드로 작성 가능 (Python 메서드로 작성)
        - 타입 체킹, 자동완성 지원
    
    - **SQLModel: ORM 라이브러리**
    - Pydantic + SQLAlchemy 통합 (내부적으로 SQLAlchemy 사용)
    - 타입 힌트 기반 (더 간결)
    - FastAPI와 완벽 호환
    - 데이터 검증 자동화


- 비유:
    - SQLite = 엑셀 파일 (데이터 저장소)
    - SQLAlchemy = 엑셀을 다루는 Python 라이브러리 (openpyxl 같은)

- 



<br>
<br>






## Security

- **One-way Hash Encryption 단방향 해시 암호화 방식들**:
    - **md5**: 아주 예전 방식, 위험함
    - **SHA family**: 빠르지만 비밀번호용으로는 살짝 위험
    - **scrypt**: 일부러 느리게 만든 방식
    - **bcrypt**: 메모리도 많이 필요하기 만든 방식. "블로피시"라는 암호화 알고리즘 기반. 일부러 느리게 만들어서 해커가 수백만 번 시도하기 힘들게 함. 같은 비밀번호여도 매번 다른 결과 (salt 사용)
    - ❓SALT

- **Authentication 인증**: "누구인가?" 사용자의 신원을 확인(=식별)
- **Authorization 인가**: "권한이 있는가?" 사용자와 제작자 사이에 프로그램 사용 권한을 주고받는 것 - 접근 권한을 허가받는 것.







<br>
<br>






## FastAPI and Server Development

<details>
<summary>Client-Server-FastAPI-DB 구조/순서</summary>

```
[클라이언트(브라우저)]
        ↕ HTTP 통신
[uvicorn 서버] ← 네트워크 담당
        ↕ 함수 호출
[FastAPI 앱] ← 비즈니스 로직 담당
        ↕ 데이터베이스 접근
[데이터베이스]
```

```
uvicorn 파싱:
원시 바이트 → 구조화된 딕셔너리
(HTTP 프로토콜 해석)

FastAPI 파싱:
구조화된 딕셔너리 → Python 객체
(애플리케이션 로직에 맞게 변환 및 검증)
```


1. 서버 시작<br>
   `$ uvicorn main:app --reload`
   
2. uvicorn: `main.py` 임포트
   - FastAPI 인스턴스(app) 로드
   - `@app.get` 데코레이터들 실행
   - FastAPI 내부에 라우팅 테이블 생성
   
3. uvicorn: 8000번 포트 열고 대기
   
4. 클라이언트: `GET /users` 요청
   
5. uvicorn: TCP 연결 수락
   
6. uvicorn: HTTP 요청 파싱<br>
    ```
    method = "GET"
    path = "/users"
    headers = {...}
    ```
   
7. uvicorn → FastAPI: 파싱된 데이터 전달
   
8. FastAPI: 라우팅 테이블 조회<br>
   `("GET", "/users") → get_users` 함수 발견
   
9. FastAPI: `get_users()` 실행

10. FastAPI: 결과를 표준 형식으로 변환<br>
    `{"users": [...]} → JSON 문자열`
    
11. FastAPI → uvicorn: 변환된 결과 반환
    
12. uvicorn: HTTP 응답 생성<br>
    ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {"users": [...]}
    ```
    
13. uvicorn: 클라이언트에게 전송
    
14. uvicorn: 다음 요청 대기 (3번으로)

</details>


- ❓TCP


- **Web server 웹서버가 하는 일**
    1. 네트워크 소켓 열기: 포트 열고 대기 / OS의 네트워크 스택과 통신
    2. HTTP 요청 수신
    3. HTTP 메시지 파싱
    4. FastAPI 호출: 3에서 파싱한 데이터를 FastAPI에게 전달
    5. HTTP 응답 생성 및 전송: FastAPI가 반환한 결과를 HTTP 형식으로 변환하여 전송

- **FastAPI가 하는 일**
    0. 애플리케이션 정의
    1. 라우팅 규칙 정의 (데코레이터를 통해 엔드포인트 정의)
    2. Request data (요청 데이터) 파싱/검증
    3. Response data (응답 데이터) 변환 - dict->json
    4. API 문서 자동 생성 - /docs 엔드포인트 생성



1. **`gunicorn`: 동기 웹서버**
    - **WSGI (Web Server Gateway Interface)** 방식: 한 번에 하나씩 순서대로 처리하는(동기) 웹서버-웹프로그램 상호작용 표준 인터페이스. (Flask, Django)
    - **pre-fork 프리포크**: 서버를 시작할 때 여러 개의 프로세스(일꾼)를 미리 만들어 둔다. 요청이 들어오면 놀고 있는 일꾼이 바로 처리한다.
    
2. **`uvicorn`: 비동기 웹서버**
    - **ASGI (Asynchronous Server Gateway Interface)** 방식: 여러 개를 동시에 처리하는(비동기) 웹서버-웹프로그램 상호작용 표준 인터페이스. (FastAPI)



- **FastAPI**: Python 기반 웹 프레임워크<br>

    - ASGI 방식을 따름 - uvicorn 권장.
    - 내부적으로 Starlette(웹 프레임워크)와 Pydantic(데이터 검증) 활용.
    - 파이썬 데코레이터를 통해 엔드포인트 정의 기능 및 템플릿 제공.
    - **Decorator 데코레이터**: 인자로 받은 함수를 감싸는 래퍼(wrapper) 함수
        ```py
        @deco
        def func(): functioning
        ```
        ==<br>
        ```
        func = deco(func)
        ```

    1. HTTP 메서드 데코레이터 (8개)<br>
        > `@app.get(), @app.post(), @app.put(), @app.delete(), @app.patch(), @app.options(), @app.head(), @app.trace()`
    2. 이벤트 핸들러 데코레이터: `@app.on_event()`
    3. 미들웨어 데코레이터: `@app.middleware()`
    4. 예외 핸들러 데코레이터: `@app.exception_handler()`
    5. WebSocket 데코레이터; `@app.websocket()`
    6. 의존성 데코레이터 (FastAPI 전용 유틸리티): `Depends()` (데코레이터처럼 사용되지만 함수)



|     개념      | C++ (컴파일/링크) | FastAPI (웹 서버)         |
|--------------|----------------|--------------------------|
| **작성**      | 소스코드 작성      | 엔드포인트 정의 (`@app.get`) |
| **변환 주체**  | 컴파일러          | 파이썬 인터프리터            |
| **테이블 생성** | 링커 (심볼 테이블) | FastAPI 객체 (라우터 테이블) |
| **실행 주체**  | OS             | uvicorn (ASGI 서버)       |
| **결과물**     | 실행 파일        | 서버 프로세스               |



- **API  (Application Programming Interface)**: 클라이언트가 서버에게 "이런 데이터 주세요"라고 요청하는, 서버별로 다르게 약속된 방식. 해당 서버의 기능을 외부에서 사용할 수 있게 해주는 창구.
    - 손님은 주방이 어떻게 요리하는지 몰라도 됨. 메뉴판만 보고 주문하면 됨.
    - **API Spec**: 레고 박스에 있는 블록의 크기, 모양, 색상 등을 표시한 명세서
    - **API doc**: 레고의 기능, 사용 방법, 호환성을 기록한 명세서
    - **라이브러리**: 레고 그자체
    - 즉, API(명세서)를 기반으로 구현된 구현체가 바로 라이브러리(레고)
   
- **Framework 프레임워크**: 개발에 필요한 기본적인 기능과 규칙을 제공해 개발 과정을 단순화시켜주는 도구.
    - "어떻게" 애플리케이션을 개발할지에 대한 지침과 틀을 제공.
    - 프레임워크가 주도권을 가짐 (프레임워크가 개발자의 코드를 호출함).
    - 정해진 구조에 맞춰서 개발자가 내용을 채움.

- **Library 라이브러리**: 개발에 필요한 기능을 호출해 재사용할 수 있는 코드의 집합.
    - "무엇을" 할 수 있는지에 대한 수단 제공.
    - 개발자가 주도권을 가짐 (개발자가 필요할 때 호출함).

- **Pydantic Model**: 데이터 계약서 + 자동 검증기 + 변환기
    - 데이터 계약서: "이 데이터는 이런 형태여야 한다"는 계약서 / 템플릿.
    - 자동 검증기 & 변환기:
    1) 타입 검증 (Type Validation): 
    2) 타입 변환 (Type Coercion): ✨일반 타입 검사기와 다른 점! 가능하면 자동 변환 - ex. 숫자 문자열을 정수로 변환
    3) 데이터 검증 (Data Validation): 타입 외의 추가 검증 - 형식, 길이, 범위 등 체크
        ```py
        class User(BaseModel):
            name: str = Field(min_length=2, max_length=50)
            age: int = Field(ge=0, le=150)  # ge = greater or equal
            email: str
            
            @validator('email')
            def validate_email(cls, v):
                if '@' not in v:
                    raise ValueError('이메일 형식이 아닙니다')
                return v
        ```
    4) 직렬화/역직렬화 (Serialization): Python 객체 ↔ JSON 변환
    
    - **C++ struct**: 정적 타입, 실행 전 컴파일러가 미리 검사 (컴파일 타임)
    - **Python dict**: 동적 타입, 검증 없음.
    - **Pydantic**: 동적 타입, 실행 중에 검사 + 변환 (런타임)







<br>
<br>






## Session and Cookie

- **stateful 상태 유지/보존**: Response 후에도 이전 Request 정보(상태)를 가지고 있음.
- **stateless 상테 없음/무상태**: Response 후 이전 Request 정보(상태)를 잊는다. - 서버가 동시에 여러 요청 처리 용이
- **connectionless 비연결성**: Response 후 아예 연결을 끊는다. - 서버가 동시에 여러 사용자(클라이언트) 처리 용이

- **Session 세션**:
    - 서버에 저장되는 정보. 쿠키보다 더 안전함 (중요한 정보는 서버에)
    - 컴퓨터 프로세스들 사이에서, 서로를 인식한 후 데이터 송수신을 마칠 때까지의 기간.
    - 사용자별 고유 식별자(세션ID)를 생성해 사용자의 정보를 저장하고, 브라우저는 이 세션ID를 사용해서 서버와 통신.
    - 세션과 관련된 정보를, 쿠키를 이용해 유저의 컴퓨터에 작은 파일로 저장을 해두고, 쿠키에 있는 세션 정보를 가지고 서버에 접근하는 방식.
    - 저장 정보 예시: 로그인한 사용자 ID, 장바구니 내용, 임시 저장 데이터, 결제 진행 상태


- **Cookie 쿠키**:
    - 서버에서 사용자의 컴퓨터(브라우저)에 설치되는 작은 기록 정보 (텍스트) 파일.
    - 웹사이트의 방문 정보를 기억해서 개인화 서비스를 제공하려는 목적으로 사용됨.
    - 서버에 저장할 필요는 없지만, 유저들이 저장하고 싶은 정보들(오늘 하루 보지 않기, 아이디 저장 등)을 저장하는 기능
    - 저장 정보 예시: 세션 아이디, 언어 설정 (작고 중요하지 않음), 테마 설정 (다크모드 등), 광고 동의 여부

- **Web storage 웹스토리지**: 브라우저 안의 개인 금고. 쿠키보다 더 많은 데이터를 브라우저에 저장할 수 있다.
    - **Local Storage 로컬 스토리지**: 영구 보관함. 직접 지우지 않으면 계속 남아 있음. (예: 사용자 설정, 테마(다크모드))
    - **Session Storage 세션 스토리지**: 임시 보관함. 브라우저 탭을 닫으면 사라짐. (예: 임시 작성 중인 글, 일회용 데이터x
- ❓**CSRF 공격**: `same_size=”lax”`로 방지

---

```
1. 사용자가 브라우저에서 버튼 클릭 (Client Side - JavaScript)
   ↓
2. API 요청 전송 (쿠키에 세션 ID 포함)
   ↓
3. 웹 서버(Uvicorn)가 요청 받음
   ↓
4. ASGI를 통해 FastAPI로 전달
   ↓
5. FastAPI가 인증/인가 확인 (bcrypt로 암호화된 비밀번호 검증)
   ↓
6. 데이터 처리 (Server Side - Python)
   ↓
7. Response 생성하여 반환
   ↓
8. 브라우저가 받아서 화면에 표시 (Client Side)
```







<br>
<br>






## Advanced Features

- **Paging 페이징**: 데이터를 한 번에 처리할 수 있는 적당한 크기로 나눠서 페이지 단위로 처리
    - 사용자가 한 번에 볼 만큼의 데이터를 조금씩 나눠서 보여줌
    - 한정된 용량에서 클라이언트, 서버 부하를 줄이기 위해 사용
    - ex) 보이는 게시글을 n개로 제한하고, 다음 게시글을 볼 수 있는 인덱스=네비게이션(고유명사로 '페이지네이션')을 제공.
    - **FastAPI-paging**: `offset`값과 `limit`값

- **Log 로그**: 컴퓨터 등에 접속한 기록 등이 컴퓨터 내에 남아있는 것
- **Log file 로그 파일**: 운영체제나 다른 소프트웨어가 실행 중에 발생하는 이벤트나 각기 다른 사용자의 통신 소프트웨어 간의 메시지를 기록한 파일
    - 에러 로그 / SQL 로그 / 접속 로그 (HTTP) / 이벤트 로그 (API 통신 로그)
    - 에러, sql, 접속, 이벤트 등 여러가지 상황이 실행되거나 실행된 후에 로그를 볼 수 있도록 파일로 남긴다.

- **REST API**: REST 아키텍처 스타일을 따르는 응용 프로그램 인터페이스.
    - **REST: Representational State Transfer 표현적 상태 전송**
    - 자원(Resource)을 URL로 표현하고, HTTP 메서드로 행위를 나타내는 설계(주로 네이밍) 원칙.

    **RESTful API Architecture Style 아키텍처 스타일 / 설계 원칙:**
    1. 리소스명은 동사가 아닌 명사를 사용한다.
    2. 자원의 행위는 HTTP 메소드로 한다.
    3. 슬래시(/)는 계층관계를 나타낼 떄 사용한다.
    - 소문자를 쓴다.
    - 밑줄(_) 말고 하이픈(-)을 쓴다.
    - 확장자(.txt 등)를 사용하지 않는다.
    - URL의 마지막에 슬래시(/)를 포함하지 않는다.
    - 등등...

   - **Idempotent (멱등성)**: GET, PUT, DELETE - 여러 번 호출해도 결과 동일
   - **Non-idempotent**: POST, PATCH - 호출 시마다 결과 달라질 수 있음

- **Design Pattern 디자인패턴**: 자주 사용하는 설계 형태를 템플릿으로 만들어둔 것. ❓어떤 종류가 있나? (그놈의 싱글톤)


- **JSONResponse**
    - 일반적인 프로세스: data -> jsonable_encoder(data):JSON 직렬화 -> data.json -> byte화 -> HTTP message (bytes)
    - JSONResponse: data -> JSONResponse(data) -> HTTP message (bytes)

    <details>
    <summary>상황별 최적 Response 선택</summary>

    ```py
    # 1. 일반 API 응답 (대부분의 경우)
    @app.get("/api")
    def api():
        return {"data": "value"}  # 자동으로 JSONResponse

    # 2. 성능이 중요한 대용량 JSON
    @app.get("/large", response_class=ORJSONResponse)
    def large_data():
        return {"items": [...]}  # 수천~수만 개 항목

    # 3. HTML 페이지 반환
    @app.get("/page", response_class=HTMLResponse)
    def page():
        return "<html>...</html>"

    # 4. 대용량 파일 다운로드
    @app.get("/download")
    def download():
        return FileResponse("large_file.zip")

    # 5. 실시간 데이터 스트리밍
    @app.get("/logs")
    def logs():
        return StreamingResponse(log_generator())

    # 6. 리다이렉트
    @app.get("/old-path")
    def redirect():
        return RedirectResponse("/new-path")
    ```
    </details>
    <br>




- ❓이벤트/예외 핸들러
- ❓미들웨어(Middleware)
    - ❓타임아웃 미들웨어
    - ❓rate-limit 미들웨어
    - ❓CORSMiddleware
    - 횡단관심사, 인증, 로깅, CORS, Rate Limiting
- ❓CORS: 브라우저 개발자 도구 Network 탭에서 응답 헤더 확인
- ❓Rate Limiting: 1분간 11회 이상 요청하여 429 에러 확인




- ❓Custom Validators
- ❓Field Validators
- ❓Root Validators
- ❓Nested Models
- ❓Union Types
- ❓Type Checking vs Runtime Validation
- ❓Mypy (Python 정적 타입 체커)
- ❓Type Annotations
- ❓Gradual Typing
- ❓Static Analysis Tools







<br>
<br>






## Model Serving
- temperature: AI 응답의 창의성/무작위성 정도 (0:결정적 ~ 1:창의적)
- max_tokens: AI가 생성할 최대 토큰(단어) 수
- top_p: 다음 단어 선택 범위 조절 (nucleus sampling)

- ❓외부 API 호출 / OpenRouter
- ❓비동기 프로그래밍 (async/await)
- ❓BackgroundTasks (백그라운드 작업)
- ❓환경변수 관리 (.env 파일 / dot.env)

- ❓WebSocket