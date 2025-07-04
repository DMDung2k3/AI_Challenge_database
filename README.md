**README - A\_C-main Project**

## 1. Tổng quan dự án

Dự án **A\_C-main** là một hệ thống backend và frontend tích hợp để xử lý và lưu trữ dữ liệu video, cung cấp API RESTful cho các chức năng chính như chat, upload video, quản lý người dùng, và phân tích video. Hệ thống sử dụng FastAPI cho backend, React cho frontend, PostgreSQL/Redis/LanceDB cho lưu trữ dữ liệu, và Docker Compose để triển khai.

## Database Architecture

Dưới đây là sơ đồ minh họa kiến trúc tương tác chính của cơ sở dữ liệu:

### PostgreSQL

```text
[API Routers] -> [Services] -> [ORM (SQLAlchemy)] -> [PostgreSQL]
    ↑                        ↓                ↑
    └─── CRUD requests       └─── query results ─┘
```

### Redis

```text
[Auth/Ratelimit Middleware] <-> [Redis Cache]
       ↑             ↓
JWT tokens, session data, rate-limit keys
```

### LanceDB

```text
[video_service / scripts/preprocess_videos.py] -> [LanceDB]
      ↑                                    ↓
      └── embedding vectors    └── similarity search results ──> [video search endpoint]
```

### Graph DB (nếu sử dụng)

```text
[RetrievalAgent] -> [GraphDB]
       ↑               ↓
 graph queries    graph responses
```

## 2. Yêu cầu trước khi cài đặt Yêu cầu trước khi cài đặt

* Python 3.10+
* Node.js 16+ và npm hoặc Yarn
* Docker và Docker Compose
* PostgreSQL, Redis (nếu chạy local không qua Docker)
* **psql (PostgreSQL CLI)** để thao tác trực tiếp với database (tùy chọn nhưng khuyến nghị cài đặt)
* ALEMBIC để quản lý migration

## 3. Cấu hình môi trường Cấu hình môi trường

1. Clone repository:

   ```bash
   git clone https://github.com/your-org/A_C-main.git
   cd A_C-main
   ```
2. Tạo file `.env` theo mẫu:

   ```dotenv
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=app_db
   REDIS_URL=redis://localhost:6379/0
   JWT_SECRET_KEY=your_jwt_secret
   ```
3. (Tùy chọn) Khởi động PostgreSQL và Redis qua Docker:

   ```bash
   docker-compose -f config/deployment/docker-compose.yml up -d
   ```

## 4. Cài đặt backend

1. Tạo và kích hoạt virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # hoặc  
   venv\Scripts\activate    # Windows PowerShell
   ```
2. Cài đặt dependencies:

   ```bash
   pip install -r requirements.txt
   pip install fastapi[all] uvicorn[standard]  # đảm bảo FastAPI và Uvicorn được cài đặt
   ```
3. Thiết lập database:

   ```bash
   alembic upgrade head
   ```

## 5. Chạy API server Chạy API server

Trước khi chạy server, hãy đảm bảo đã cài `uvicorn`:

```bash
pip install uvicorn[standard]
```

**Chạy API server:**

* Trên Linux/Mac hoặc khi `uvicorn` đã được thêm vào PATH:

  ```bash
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
  ```
* Trên Windows PowerShell hoặc khi lệnh `uvicorn` không nhận dạng được:

  ```powershell
  python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
  ```

Sau khi khởi chạy thành công, truy cập tài liệu API tại `http://localhost:8000/docs`.## 6. Cài đặt và chạy frontend

1. Vào thư mục frontend:

   ```bash
   cd frontend
   ```
2. Cài đặt gói npm:

   ```bash
   npm install
   ```
3. Chạy ứng dụng React:

   ```bash
   npm start
   ```

Mở trình duyệt tại `http://localhost:3000`.

## 7. Chạy các script hỗ trợ

* Tiền xử lý video:

  ```bash
  python scripts/preprocess_videos.py --input-folder data/raw --output-folder data/processed
  ```
* Tạo seed demo data:

  ```bash
  python scripts/seed_demo.py
  ```
* Benchmark:

  ```bash
  python scripts/benchmark.py
  ```

## 8. Kiểm thử

Chạy toàn bộ test suite bằng pytest:

```bash
pytest --maxfail=1 --disable-warnings -q
```

## 9. Triển khai

Sử dụng Docker Compose để triển khai toàn bộ dịch vụ:

```bash
docker-compose -f config/deployment/docker-compose.yml up --build -d
```

Cấu hình Prometheus monitoring cũng nằm trong `config/deployment/prometheus.yml`.

## 10. Cấu trúc thư mục chính

```
A_C-main/
├── api/                    # Backend FastAPI
├── agents/                 # Các agent điều phối hội thoại
├── config/deployment/      # Docker Compose, Prometheus
├── data/                   # LanceDB lưu vector video
├── database/               # Kết nối DB, migrations, ORM models
├── frontend/               # React client
├── scripts/                # Các script hỗ trợ
├── static/                 # Tài nguyên tĩnh
├── test/                   # Unit, integration, e2e tests
└── tools/                  # Các công cụ nội bộ
```

#### 10.1 Cấu trúc thư mục `database/`

```
database/
├── connections/           # Các module kết nối đến các hệ quản trị DB
│   ├── bloom_filter.py    # Kết nối và cấu hình bloom filter
│   ├── cache_db.py        # Kết nối Redis cache
│   ├── graph_db.py        # Kết nối Graph DB (Neo4j)
│   ├── metadata_db.py     # Kết nối PostgreSQL metadata
│   └── vector_db.py       # Kết nối LanceDB vector
├── migrations/            # Alembic migrations
│   └── versions/
│       ├── 001_initial.py
│       ├── 002_add_vectors.py
│       └── 003_add_sessions.py
└── models/                # ORM models
    ├── base.py            # Base declarative
    ├── conversation.py    # Model Conversation
    ├── processing_job.py  # Model ProcessingJob
    ├── user_session.py    # Model UserSession
    └── video_metadata.py  # Model VideoMetadata
```

A\_C-main/ ├── api/                    # Backend FastAPI ├── agents/                 # Các agent điều phối hội thoại ├── config/deployment/      # Docker Compose, Prometheus ├── data/                   # LanceDB lưu vector video ├── database/               # Kết nối DB, migrations, ORM models ├── frontend/               # React client ├── scripts/                # Các script hỗ trợ ├── static/                 # Tài nguyên tĩnh ├── test/                   # Unit, integration, e2e tests └── tools/                  # Các công cụ nội bộ

````

---

## 11. Phân tích cơ sở dữ liệu

Phần **database/** chịu trách nhiệm lưu trữ, truy vấn và quản lý toàn bộ dữ liệu quan trọng của hệ thống, bao gồm:

1. **Connections (kết nối)**
   - Các module trong `database/connections/` (ví dụ `metadata_db.py`, `vector_db.py`, `cache_db.py`, `graph_db.py`) khởi tạo và cung cấp các kết nối tới:
     - **PostgreSQL**: lưu các bảng quan hệ dùng cho người dùng, session, lịch sử chat, metadata video. (đầu ra: đối tượng `SessionLocal` để thao tác ORM).
     - **Redis**: dùng làm cache phiên người dùng, rate limit, token JWT. (đầu vào/đầu ra: các key-value trong Redis).
     - **LanceDB**: lưu trữ vector embedding của video (đầu vào: embedding từ quá trình xử lý, đầu ra: tìm kiếm tương đồng vector).
     - **Graph DB** (nếu sử dụng): quản lý quan hệ đồ thị nâng cao (trong tương lai).

2. **ORM Models**
   - Các file trong `database/models/` (ví dụ `user_session.py`, `conversation.py`, `video_metadata.py`, `processing_job.py`) mô tả cấu trúc bảng:
     - `User`: thông tin tài khoản (id, email, hashed_password, role).
     - `UserSession`: phiên đăng nhập (session_id, user_id, expires_at).
     - `Conversation`: lưu lịch sử chat (message_id, session_id, content, timestamp).
     - `VideoMetadata`: lưu thông tin video (video_id, user_id, filename, duration, upload_time).
     - `ProcessingJob`: theo dõi các job tiền xử lý hoặc phân tích video (job_id, video_id, status, result_path).

3. **Migrations**
   - Thư mục `database/migrations/versions/` chứa các tập lệnh Alembic:
     - `001_initial.py`: tạo các bảng cơ bản.
     - `002_add_vectors.py`: thêm cột vector embedding vào `VideoMetadata`.
     - `003_add_sessions.py`: thêm bảng `UserSession`.

4. **Luồng dữ liệu (Data Flow)**
   - Khi **API router** (`api/routers/*.py`) nhận request:
     - Ví dụ `upload.py` gọi service `video_service.py` tạo bản ghi `VideoMetadata` qua ORM (đầu ra: INSERT vào PostgreSQL).
     - Service sau đó tiền xử lý video (`scripts/preprocess_videos.py`), tạo embedding và lưu vào LanceDB (đầu ra: vector lưu LanceDB).
   - Khi người dùng chat qua endpoint `/chat`:
     - Router `chat.py` gọi `ChatService`, dùng `ConversationOrchestrator` xử lý, đồng thời lưu mỗi message vào bảng `Conversation` (đầu ra: INSERT vào PostgreSQL).
     - Kết quả trả về client và có thể được cache tạm thời vào Redis (đầu vào/đầu ra: Redis).
   - Các truy vấn metadata video (endpoint `/videos`) sẽ lấy dữ liệu từ PostgreSQL, kết hợp với kết quả tìm kiếm vector từ LanceDB (đầu vào: vector query, đầu ra: danh sách video tương đồng).

5. **Đầu vào/Đầu ra của Database**
   - **Đầu vào**:
     - Dòng lệnh migration (`alembic upgrade head`).
     - Các lệnh CRUD ORM từ `api/services/*_service.py`.
     - Script `seed_demo.py` tạo dữ liệu mẫu.
   - **Đầu ra**:
     - API response JSON chứa dữ liệu từ database.
     - File log migrations và schema.
     - Cache trong Redis cho các phiên và rate limit.


Mục này giúp bạn hình dung toàn bộ cách database tích hợp với backend, services, và các hệ thống lưu trữ vector/caching khác.

## 12. Kiến trúc tương tác của Database

Dưới đây là sơ đồ kiến trúc minh họa cách mỗi database giao tiếp với các thành phần liên quan:

### PostgreSQL
```text
[API Routers] -> [Services] -> [ORM (SQLAlchemy)] -> [PostgreSQL]
    ↑                        ↓                ↑
    └─── CRUD requests       └─── query results ─┘
````

* **Đầu vào**: Các lệnh CRUD từ `api/routers` thông qua `services` và ORM.
* **Đầu ra**: Kết quả truy vấn trả về Services → Routers → Client.

### Redis

```text
[Auth/Ratelimit Middleware] <-> [Redis Cache]
       ↑             ↓
JWT tokens, session data, rate-limit keys
```

* **Đầu vào**: Lưu trữ và truy xuất token JWT, thông tin session, counters rate-limit.
* **Đầu ra**: Trả về thông tin phiên, xác thực, và tính toán rate-limit.

### LanceDB

```text
[video_service / scripts/preprocess_videos.py] -> [LanceDB]
      ↑                                    ↓
      └── embedding vectors    └── similarity search results ──> [video search endpoint]
```

* **Đầu vào**: Vector embedding từ quá trình tiền xử lý video.
* **Đầu ra**: Kết quả tìm kiếm tương đồng được trả về qua API.

### Graph DB (nếu sử dụng)

```text
[RetrievalAgent] -> [GraphDB]
       ↑               ↓
 graph queries    graph responses
```

* **Đầu vào**: Truy vấn node/edge cho kiến thức đồ thị.
* **Đầu ra**: Kết quả truy vấn để hỗ trợ agent trả lời.

## 13. Chạy test và khảo sát Database

### 13.1. Chuẩn bị môi trường

* Đảm bảo các dịch vụ DB đang chạy (hoặc khởi động qua Docker Compose):

  ```bash
  docker-compose -f config/deployment/docker-compose.yml up -d postgres redis
  ```

### 13.2. Chạy test tổng quan cho Database

```bash
pytest test/test_connections.py test/test_connections_redis.py test/test_models.py test/integration/test_preprocessing_pipeline.py
```

* `test_connections.py`: kiểm tra kết nối và CRUD với PostgreSQL.
* `test_connections_redis.py`: kiểm tra kết nối và thao tác với Redis.
* `test_models.py`: xác thực ORM models trùng khớp schema.
* `test_preprocessing_pipeline.py`: kiểm tra luồng tiền xử lý và lưu vector vào LanceDB.

### 13.3. Chạy test riêng lẻ

* **PostgreSQL**

  ```bash
  pytest test/test_connections.py test/test_models.py
  ```
* **Redis**

  ```bash
  pytest test/test_connections_redis.py
  ```
* **LanceDB**

  ```bash
  pytest test/integration/test_preprocessing_pipeline.py
  ```

Mọi thắc mắc hoặc góp ý vui lòng mở issue trên GitHub.

## 14. Khảo sát Database (Survey)

Dưới đây là các lệnh và phương pháp để khảo sát nhanh trạng thái và cấu trúc của từng database.

### 14.1. PostgreSQL

* **Trên Linux/Mac hoặc khi đã cài psql CLI**:

  ```bash
  psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt"
  psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "\d+ <table_name>"
  psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT COUNT(*) FROM <table_name>;"
  ```
* **Trên Windows PowerShell (chưa cài psql CLI)**:

  * Sử dụng PowerShell environment variables:

    ```powershell
    docker exec -it ai_challenge_postgres \
      psql -U $Env:POSTGRES_USER -d $Env:POSTGRES_DB -c "\dt"
    docker exec -it ai_challenge_postgres \
      psql -U $Env:POSTGRES_USER -d $Env:POSTGRES_DB -c "\d+ <table_name>"
    docker exec -it ai_challenge_postgres \
      psql -U $Env:POSTGRES_USER -d $Env:POSTGRES_DB -c "SELECT COUNT(*) FROM <table_name>;"
    ```
  * Hoặc thay `%POSTGRES_USER%` và `%POSTGRES_DB%` bằng giá trị thực (ví dụ `-U your_user -d app_db`):

    ```powershell
    docker exec -it ai_challenge_postgres \
      psql -U your_user -d app_db -c "\dt"
    ```

### 14.2. Redis. Redis. Redis

* **Kiểm tra kết nối**:

  ```bash
  redis-cli -u $REDIS_URL ping
  ```
* **Liệt kê key**:

  ```bash
  redis-cli -u $REDIS_URL keys "*"
  ```
* **Lấy giá trị key cụ thể**:

  ```bash
  redis-cli -u $REDIS_URL get <key_name>
  ```

### 14.3. LanceDB

* **Khởi tạo client và khảo sát**:

  ```python
  from lancedb import connect
  db = connect("./data/lancedb/video_vectors.lance")
  table = db.table("video_vectors")
  print(table.schema)
  print(table.count())
  ```
* **Thực hiện truy vấn tương đồng**:

  ```python
  vec = [...]  # vector sample
  results = table.search(vec, limit=5)
  print(results)
  ```

### 14.4. Neo4j (GraphDB, nếu sử dụng)

* **Đếm số node**:

  ```cypher
  MATCH (n) RETURN count(n);
  ```
* **Đếm số relationship**:

  ```cypher
  MATCH ()-[r]->() RETURN count(r);
  ```

## 15. Các file cần chỉnh sửa và cài đặt

Để chạy hệ thống và thao tác database thành công, bạn cần đảm bảo và chỉnh sửa các file sau:

1. **.env**

   * Đặt các biến môi trường: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `REDIS_URL`, `JWT_SECRET_KEY`.
   * File này thường nằm ở root của project.

2. **requirements.txt**

   * Đảm bảo có các dependencies quan trọng:

     ```text
     fastapi[all]
     uvicorn[standard]
     sqlalchemy
     psycopg2-binary
     redis
     lancedb
     alembic
     ```
   * Sau khi chỉnh sửa, chạy `pip install -r requirements.txt`.

3. **config/deployment/docker-compose.yml**

   * Kiểm tra tên service và container (ví dụ `ai_challenge_postgres`, `ai_challenge_redis`).
   * Xác nhận port mapping (`5432:5432`, `6379:6379`).
   * Cập nhật volume nếu cần giữ persist data.

4. **alembic.ini**

   * Thiết lập `sqlalchemy.url` trỏ đúng tới database (có thể dùng biến môi trường trong file `.env`).

5. **api/agents/orchestrator/conversation\_orchestrator.py** (nếu bạn đã tùy chỉnh logic agent)

   * Thêm hoặc sửa phương thức `process()` để tránh lỗi abstract.

6. **api/services/**

   * Bạn có thể thêm hoặc sửa các service liên quan database (ví dụ `video_service.py`, `chat_service.py`) để đảm bảo các CRUD hoạt động đúng.

7. **scripts/preprocess\_videos.py**

   * Kiểm tra đường dẫn input/output và kết nối tới LanceDB.

8. **Dockerfile** (nếu có trong project)

   * Xác nhận cài đặt `psycopg2-binary` và `postgresql-client` nếu bạn muốn sử dụng `psql` trong container.

Sau khi chỉnh sửa các file trên, hãy khởi động lại Docker Compose, cập nhật migration (`alembic upgrade head`), và chạy lại server để đảm bảo mọi thay đổi được áp dụng.
