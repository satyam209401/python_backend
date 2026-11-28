# 🚀 Python Backend API Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-Async%20Ready-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![Security](https://img.shields.io/badge/Security-AES--256--GCM%20%7C%20Argon2id%20%7C%20Ed25519-green.svg)](https://owasp.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Modular%20%7C%20Auto--Routing-orange.svg)](#)

A high-performance, modular, and enterprise-grade Python backend framework built on top of **FastAPI**, **SlowAPI**, and **Uvicorn**. Designed for rapid microservices and scalable web applications with zero-boilerplate auto-routing, built-in cryptographic security, universal database connectors, and production-ready audit logging.

---

## 📑 Table of Contents

- [📁 Project Folder Structure & Architecture](#-project-folder-structure--architecture)
- [1. Environment Configuration (`env`)](#1-environment-configuration-env)
- [2. API Response Helper (`res`)](#2-api-response-helper-res)
- [3. Request Body Limiter (`body`)](#3-request-body-limiter-body)
- [4. Logger Utility (`log`)](#4-logger-utility-log)
- [5. Client & User Info Utility (`user_info`)](#5-client--user-info-utility-user_info)
- [6. Database Manager (`DB.raw`, `DB.isConnected`)](#6-database-manager-dbraw-dbisconnected)
- [7. SQLite Web Viewer (`sqlite.view`)](#7-sqlite-web-viewer-sqliteview)
- [8. Request Accessor (`req`)](#8-request-accessor-req)
- [9. Security & Cryptography Utilities](#9-security--cryptography-utilities)
  - [9.1 AES-256-GCM Encryption (`aes`)](#91-aes-256-gcm-encryption-aes)
  - [9.2 Base64 Helper (`base`)](#92-base64-helper-base)
  - [9.3 OWASP Password Hashing (`password`)](#93-owasp-password-hashing-password)
  - [9.4 Stateless Encrypted Token & Unique Token Generator (`token`)](#94-stateless-encrypted-token-manager-token)
  - [9.5 Ed25519 Digital Signature (`dsc`, `dscToken`, `dscVerify`)](#95-ed25519-digital-signature-dsc-dsctoken-dscverify)
- [10. Anti-Exploit String Validator (`GuardString`)](#10-anti-exploit-string-validator-guardstring)
- [11. Main API Entry Gate (`entry`)](#11-main-api-entry-gate-entry)
- [12. Asynchronous Redis Client (`redis`)](#12-asynchronous-redis-client-redis)
- [13. CORS Configuration (`cors`)](#13-cors-configuration-cors)
- [14. Complete API Endpoint Guide (Step-by-Step with SlowAPI)](#14-complete-api-endpoint-guide-step-by-step-with-slowapi)
- [15. Zero-Dependency HTTP Client (`http`)](#15-zero-dependency-http-client-http)
- [🚀 How to Run the Project (Step-by-Step Guide)](#how-to-run-the-project-project-run-kaise-karein)

---

## 📁 Project Folder Structure & Architecture

Yeh framework **Modular Architecture** follow karta hai jisme sabhi core utilities globally inject hoti hain (`builtins`), jisse endpoints me redundant imports nahi karne padte:

```text
py_backend/
├── .env                          # Local environment variables (Git ignored)
├── .env.example                  # Environment template file
├── .gitignore                    # Git tracking ignore rules (.venv, .env, *.sqlite, logs)
├── env.py                        # Centralized environment loader (builtins.env)
├── main.py                       # Application bootstrap & ASGI Uvicorn server entry
├── README.md                     # Comprehensive framework & API documentation
├── requirements.txt              # Project dependencies manifest
│
├── App/                          # Core Framework Engine & Global Registrations
│   ├── app.py                    # FastAPI setup, middleware stack, lifespan & builtins injection
│   ├── entry.py                  # Global /api entry gate router & middleware proxy
│   │
│   ├── database/                 # Database Drivers & Connection Pools
│   │   ├── redis.py              # Asynchronous Redis client with auto JSON serialization
│   │   ├── sql.py                # Multi-engine SQL manager (SQLite, MySQL, PostgreSQL)
│   │   └── sqlite_web.py         # Built-in SQLite web management viewer
│   │
│   ├── exception_handler/        # Centralized Exception Interceptors
│   │   ├── __init__.py           # Exception handler registry
│   │   ├── http.py               # Custom HTTP status error formatting
│   │   ├── rate_limit.py         # SlowAPI 429 Too Many Requests interceptor
│   │   ├── server.py             # Global 500 unhandled exception & AuditLogger trigger
│   │   └── validation.py         # Pydantic & request payload validation handler
│   │
│   ├── security/                 # Cryptography & Protection Modules
│   │   ├── cors.py               # Dynamic CORS policy builder
│   │   ├── password.py           # OWASP-compliant Argon2id password hasher
│   │   ├── token.py              # Stateless encrypted token & CSPRNG token generator
│   │   │
│   │   ├── aes/                  # AES-256-GCM Authenticated Encryption
│   │   │   ├── enc.py            # Payload encryption with dynamic IV
│   │   │   └── dec.py            # Authenticated decryption with tag verification
│   │   │
│   │   └── base64/               # URL-safe & Standard Base64 Encoding
│   │       ├── enc.py            # Base64 encoder
│   │       └── des.py            # Base64 decoder
│   │
│   └── src/                      # Internal Services, Utilities & Helpers
│       ├── router.py             # AutoRouter: File-based dynamic route discovery engine
│       │
│       ├── cleaner/              # System Cache Maintenance
│       │   └── clear_pycache.py  # Automatic __pycache__ cleanup on application boot
│       │
│       ├── dsc/                  # Asymmetric Digital Signatures
│       │   └── dsc.py            # Ed25519 high-speed keypair signer & verifier
│       │
│       ├── utils/                # Injected Global Utilities
│       │   ├── audit_logger.py   # High-throughput SQLite runtime performance logger
│       │   ├── body.py           # Request body size limiter decorator (@body.limit)
│       │   ├── http.py           # Zero-dependency HTTP client (http.get, http.post)
│       │   ├── log.py            # Daily structured JSON file logger
│       │   ├── req.py            # Request accessor (headers, client IP, params)
│       │   ├── response.py       # Standardized API response builder (res.s, res.e)
│       │   └── user_info.py      # Client IP, device, OS & browser metadata extractor
│       │
│       └── Validator/            # Input Sanitization
│           └── str.py            # Anti-exploit GuardString string validator
│
├── db/                           # Local SQLite Storage Directory (Git ignored)
│   ├── audit_logs.sqlite         # Permanent API request & execution audit records
│   └── runtime_time_log.sqlite   # Endpoint latency & runtime benchmark logs
│
├── logs/                         # Application Log Storage (Git ignored)
│   ├── app.log                   # Standard application output log
│   └── 27-11-2026.json           # Daily rotation JSON log files
│
└── routes/                       # Application API Endpoints (Auto-Discovered)
    └── user/
        └── register.py           # Example user registration endpoint with SlowAPI
```

### 🌟 Core Architectural Highlights

| Feature | Description |
| :--- | :--- |
| **Global Builtins Injection** | `env`, `res`, `req`, `log`, `body`, `user_info`, `token`, `limiter`, `DB`, `redis`, `http` pure application me bina kisi import ke directly accessible hain. |
| **Zero-Config AutoRouter** | `routes/` directory me koi bhi `.py` file add karein, wo automatically `/api/...` prefix ke saath mount ho jati hai. `main.py` ko touch karne ki jarurat nahi. |
| **Enterprise Cryptography** | AES-256-GCM, Argon2id, Ed25519 digital signatures, aur CSPRNG unique token generation out-of-the-box integrated hai. |
| **High-Throughput Audit Logging** | Har incoming request ka execution time, status code, IP, aur endpoint asynchronous SQLite database me log hota hai. |
| **Centralized Error Handling** | Standardized JSON output across 400, 401, 404, 422, 429, aur 500 status codes. |

---

## 1. Environment Configuration (`env`)

The project uses `env.py` and a globally registered `env()` helper function to manage environment variables from `.env`.

### Key Features
- **Global Availability:** Directly use `env("KEY")` anywhere in the project without importing `os` or `env`.
- **Custom Path Support:** Configure the `.env` location via `env.py` (e.g. for server or local environment).
- **Load Status Inspection (`env.is_loaded`):** Boolean flag indicating whether the `.env` file exists and was loaded successfully.
- **Bytecode Control:** Prevent Python from generating `__pycache__` directories by toggling an environment setting.

---

### Configuration (`env.py`)

File: `env.py`

```python
# Set the explicit path to your .env file
ENV_PATH = Path("/www/wwwroot/private/.env")  # Server deployment
# Local development: ENV_PATH = Path(".env")
```

---

### `.env` File Setup

Create a `.env` file in the configured location:

```env
APP_NAME=Python Backend API
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
APP_RELOAD=false


# Disable Python bytecode (__pycache__) generation
DONT_WRITE_BYTECODE=true
```

---

### Usage in Code

#### 1. Retrieve a Value
```python
# Available globally across all modules (no import needed):
app_name = env("APP_NAME")
port = env("PORT")
```

#### 2. Retrieve with a Default Fallback Value
If the requested key does not exist in `.env`, the fallback value is returned:
```python
# Returns 8000 if PORT is not found
port = env("PORT", 8000)

# Returns False if DEBUG is not found
debug_mode = env("DEBUG", False)
```

#### 3. Verify If `.env` Is Loaded (`env.is_loaded`)
```python
if not env.is_loaded:
    print("Warning: .env file is not loaded!")
```

---

## 2. API Response Helper (`res`)

The `res` helper standardizes all API JSON responses across FastAPI endpoints, ensuring uniform response structures and automatic security headers.

### Key Features
- **Global Availability:** Registered in `builtins.res`, so `res.s()` and `res.e()` are available everywhere without imports.
- **Automatic Security Headers:** Every response automatically includes:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Predictable JSON Structure:** The frontend client always receives a consistent format:
  ```json
  {
    "status": true,
    "status_code": 200,
    "message": "Response message",
    "data": []
  }
  ```
- **Flexible Argument Order & Safe Defaults:** Arguments ko kisi bhi order me pass kiya ja sakta hai (`res.s(message, data)` ya `res.s(data, message)`). Sirf message pass karne par `data` hamesha clean `[]` rehta hai.
- **Safe HTTP Header Fallback:** Custom business codes (jaise `6000`, `9001` ya large codes) pass karne par browser/Axios network crash se bachane ke liye HTTP status header safe `200` (success) ya `400` (error) par fallback hota hai, jabki JSON ke andar exact custom `status_code` rehta hai.
- **Automatic JSON String Parsing:** Agar `data` me raw JSON string (jaise Redis, database JSON column ya external API se aane wala string `'{"id": 101}'` ya `'[...]`) pass hota hai, toh `res` use automatically parse kar leta hai — aapko manually `json.loads()` karne ki jarurat nahi padti.

---

### Response Methods

#### 1. Success Response: `res.s()`
```python
# 1. Sirf message
return res.s("Profile updated successfully.")
# HTTP: 200 | JSON: {"status": true, "status_code": 200, "message": "Profile updated successfully.", "data": []}

# 2. Message + data + custom flow code (e.g., 6000)
return res.s("Two-step verification required.", {"challenge_id": "chk_98a7b6c5"}, 6000)
# HTTP: 200 | JSON: {"status": true, "status_code": 6000, "message": "Two-step verification required.", "data": {"challenge_id": "chk_98a7b6c5"}}
```

---

#### 2. Error Response: `res.e()`
```python
# 1. Unauthorized (401)
return res.e("Your session has expired. Please reopen Swarg Marg and sign in again.", 401)
# HTTP: 401 | JSON: {"status": false, "status_code": 401, "message": "Your session has expired. Please reopen Swarg Marg and sign in again.", "data": []}

# 2. Validation error with extra data (422)
return res.e("Invalid request payload.", 422, {"field": "email", "reason": "Invalid format"})
# HTTP: 422 | JSON: {"status": false, "status_code": 422, "message": "Invalid request payload.", "data": {"field": "email", "reason": "Invalid format"}}
```

---

## 3. Request Body Limiter (`body`)

The `body` utility provides endpoint-level protection against oversized payload attacks and Denial of Service (DoS) by enforcing maximum request body limits.

### Key Features
- **Global Availability:** Accessible globally as `@body.limit(...)` or explicitly via `from App.src.utils.body import body`.
- **Dual-Layer Protection:**
  1. **Header Inspection:** Rejects oversized requests immediately using `Content-Length` before consuming server memory.
  2. **Raw Byte Verification:** Enforces payload limits even if `Content-Length` is missing or spoofed.
- **Flexible Units:** Supports `B`, `KB`, `MB`, and `GB` (case-insensitive, e.g. `"500KB"`, `"2MB"`, `"10MB"`).
- **HTTP 413 Handling:** Automatically raises `HTTP 413 Request payload too large` when the threshold is exceeded.

---

### Usage in Code

Apply the `@body.limit()` decorator directly above any FastAPI route handler:

```python
from fastapi import Request

# 1. Limit JSON payload to 2MB (Global access)
@app.post("/api/update-profile")
@body.limit("2MB")
async def update_profile(request: Request):
    return res.s("Profile updated successfully")

# 2. Limit small payloads (e.g. 100KB for auth endpoints)
@app.post("/api/login")
@body.limit("100KB")
async def login(request: Request):
    return res.s("Logged in successfully")

# 3. Explicit import (if preferred)
from App.src.utils.body import body

@app.post("/api/upload")
@body.limit("10MB")
async def upload_file(request: Request):
    return res.s("File received")
```

---

### Supported Size Units

| Unit | Example | Description |
| :--- | :--- | :--- |
| `B` | `"1024B"` | Bytes |
| `KB` | `"500KB"` | Kilobytes (1024 Bytes) |
| `MB` | `"2MB"` | Megabytes (1024 x 1024 Bytes) |
| `GB` | `"1GB"` | Gigabytes (1024 x 1024 x 1024 Bytes) |

**Note:** The decorator works with both synchronous and asynchronous endpoints. The size is validated before the endpoint function executes.

---

## 4. Logger Utility (`log`)

The `log` utility provides structured, automatic file logging with timestamps, source file detection, and formatting for dictionaries, lists, and exception tracebacks.

### Key Features
- **Global Availability:** Registered in `builtins.log`, so `log(...)` can be called from any file without imports.
- **Automatic Caller Detection:** Automatically detects which file triggered the log (e.g. `[ 2026-11-27 11:57:00 ] [ login.py ]`).
- **File Output:** Saves logs into the `logs/` directory named after the calling file (e.g. `logs/login.log`, `logs/app.log`), creating folders automatically.
- **Smart Data Formatting:**
  - Strings: Logged cleanly as single-line or multi-line blocks.
  - Dictionaries / Lists: Automatically formatted as pretty-printed JSON (`indent=2`).
  - Exceptions: Automatically formats the full stack trace (`traceback.format_exception`).

---

### Usage in Code

```python
# 1. Simple text log
log("Application server started successfully")

# 2. Dictionary / JSON data logging (pretty-printed automatically)
user_data = {"user_id": 101, "email": "user@example.com", "role": "admin"}
log(user_data)

# 3. Exception / Error logging with full stack trace
try:
    result = 10 / 0
except Exception as exc:
    log(exc)

# 4. Custom log file path (optional)
log("Custom event log", path="logs/custom_audit.log")
```

---

## 5. Client & User Info Utility (`user_info`)

The `user_info` utility extracts client request metadata, including real IP addresses (with proxy and Cloudflare support), browser, operating system, and device type.

### Key Features
- **Global Availability:** Registered in `builtins.user_info`, directly accessible across endpoints.
- **Real IP Detection:** Resolves the client's true IP address, respecting trusted local reverse proxies (`127.0.0.1`, `::1`) and Cloudflare headers (`cf-connecting-ip`).
- **Device & Browser Detection:** Automatically parses user-agent strings into clean identifiers:
  - **Browsers:** Chrome, Firefox, Safari, Edge, Opera
  - **Operating Systems:** Windows, Android, iOS, macOS, Linux
  - **Devices:** Mobile, Tablet, Desktop

---

### Usage in Code

```python
from fastapi import Request

@app.get("/api/client-info")
async def get_client_info(request: Request):
    # 1. Get client IP address
    ip = user_info.ip(request)

    # 2. Get detected browser name
    browser = user_info.browser()

    # 3. Get detected operating system
    os_name = user_info.os()

    # 4. Get device category (Mobile, Tablet, Desktop)
    device = user_info.device()

    # 5. Get complete client metadata dictionary
    client_data = user_info.info()
    
    return res.s("Client info retrieved", client_data)
```

#### Example Output (`user_info.info()`):
```json
{
  "ip": "203.0.113.195",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
  "browser": "Chrome",
  "os": "Windows",
  "device": "Desktop",
  "platform": "\"Windows\"",
  "model": "",
  "mobile": "?0",
  "language": "en-US,en;q=0.9",
  "referer": null
}
```

---

## 6. Database Manager (`DB.raw`, `DB.isConnected`)

The `DB` utility in `App/database/sql.py` provides a unified, production-ready interface to run SQL queries (`DB.raw`) and verify connection health (`DB.isConnected`) across **SQLite**, **MySQL**, and **PostgreSQL** without changing your query logic.

### Supported Database Engines & Use Cases

| Database | Driver Name | Best Use Case | Key Features |
| :--- | :--- | :--- | :--- |
| **SQLite** | `"sqlite"` | Local development, single-server apps, microservices, local audit logs, zero-setup portability. | Auto-configured high-performance PRAGMAs (`WAL` journal mode, `64KB` page size, `64MB` cache, `2GB` mmap, foreign keys, busy timeout `5000ms`). |
| **MySQL / MariaDB** | `"mysql"` | High-traffic web apps, eCommerce, relational systems with high concurrent writes. | DictCursor support, utf8mb4 encoding, connection timeouts, autocommit. |
| **PostgreSQL** | `"pg"` / `"postgres"` | Enterprise systems, complex analytical queries, JSON/JSONB payloads, financial and strict ACID compliance. | DictRow row-factory, SSL mode support, parameterized colon syntax. |

---

### Configuration Setup (`.env`)

You can store database connection configurations as JSON strings in `.env` or pass configuration dictionaries directly in Python:

```env
# 1. SQLite Configuration
DB_SQLITE='{"DRIVER": "sqlite", "path": "db/audit_logs.sqlite"}'

# 2. MySQL Configuration
DB_MYSQL='{"DRIVER": "mysql", "DB_HOST": "127.0.0.1", "DB_PORT": 3306, "DB_NAME": "app_db", "DB_USER": "root", "DB_PASS": "secret", "DB_CHARSET": "utf8mb4"}'

# 3. PostgreSQL Configuration
DB_POSTGRES='{"DRIVER": "pg", "DB_HOST": "127.0.0.1", "DB_PORT": 5432, "DB_NAME": "app_pg_db", "DB_USER": "postgres", "DB_PASS": "secret", "DB_SSLMODE": "prefer"}'
```

---

### Usage in Code

#### 1. SQLite Use Case
Use SQLite when you need local, high-speed, zero-maintenance storage without running external database services:

```python
from App.database.sql import DB

# Select query (returns list of dictionaries):
users = DB.raw("DB_SQLITE", "SELECT * FROM users WHERE status = ? LIMIT 10", ["active"])

# Insert query (returns affected row count):
affected = DB.raw(
    "DB_SQLITE",
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ["Rahul Sharma", "rahul@example.com"]
)

# In-memory SQLite for testing:
test_db = {"DRIVER": "sqlite", "path": ":memory:"}
DB.raw(test_db, "CREATE TABLE temp (id INTEGER PRIMARY KEY, val TEXT)")
```

#### 2. MySQL / MariaDB Use Case
Use MySQL for relational data requiring high concurrency and web-scale performance:

```python
from App.database.sql import DB

# Using named parameters with colon syntax (:email):
user = DB.raw(
    "DB_MYSQL",
    "SELECT id, name, email FROM users WHERE email = :email",
    {"email": "rahul@example.com"}
)

# Update query:
updated_rows = DB.raw(
    "DB_MYSQL",
    "UPDATE users SET status = :status WHERE id = :user_id",
    {"status": "verified", "user_id": 101}
)
```

#### 3. PostgreSQL Use Case
Use PostgreSQL for enterprise architectures, complex joins, JSON querying, and transactional rigor:

```python
from App.database.sql import DB

# Complex query with colon parameters:
orders = DB.raw(
    "DB_POSTGRES",
    "SELECT id, total_amount, status FROM orders WHERE status = :status ORDER BY created_at DESC LIMIT 20",
    {"status": "completed"}
)

# Querying native JSON / JSONB columns:
device_logs = DB.raw(
    "DB_POSTGRES",
    "SELECT id, payload->>'browser' AS browser FROM audit_logs WHERE payload->>'user_id' = :uid",
    {"uid": "101"}
)
```

#### 4. Connection Health Check (`DB.isConnected`)
Verify database connectivity before running operations or during startup health checks (returns boolean `True` or `False`):

```python
from App.database.sql import DB  # or use global builtins: DB / db

# 1. Check MySQL connection:
if DB.isConnected(env("mysql")):
    print("MySQL connected")

# 2. Check PostgreSQL connection (env key name or config string):
ok_pg = DB.isConnected(env("pg"))

# 3. Check SQLite connection with dict or env key name:
ok_sqlite = DB.isConnected({"DRIVER": "sqlite", "path": "./data/app.db"})
if ok_sqlite:
    print("SQLite ready")
```

---

## 7. SQLite Web Viewer (`sqlite.view`)

An in-browser Adminer-style graphical management interface for SQLite databases.

### Key Features
- **Browse & Search:** Fast paginated data view (strict 100 rows per page limit).
- **CRUD Operations:** Insert, Edit, and Delete records with single confirmation alerts.
- **Table Schema & Indexing (phpMyAdmin style):**
  - Add / Drop / Change columns.
  - Set `UNIQUE` or `INDEX` directly from the structure table or column creation forms.
  - View all table indexes with a 1-click `Drop` action.
- **SQL Console:** Execute custom SQL commands with timing and row count metrics.
- **CSV Export:** 1-click export of table data to CSV.

### Endpoint Mount Example

```python
from fastapi import FastAPI
import App.app

app = FastAPI(lifespan=App.app.lifespan)
App.app.init(app)

@app.get("/db")
async def view_database():
    # Renders the full Adminer SQLite web UI for the given database file:
    return sqlite.view(env("audit_logs"))
```

---

## 8. Request Accessor (`req`)

The `req` utility provides an asynchronous, context-aware interface for extracting request body data, HTTP headers, and URL query parameters with built-in memory caching.

### Key Features
- **Global Availability:** Accessible globally via `req` without explicit imports.
- **Context-Aware:** Automatically detects the current request context or accepts an explicit `Request` object.
- **Auto Body Detection:** Automatically parses JSON, URL-encoded forms, multipart forms, or raw text based on `Content-Type`.
- **Request State Caching:** Caches parsed body data on `request.state._cached_body_data` to eliminate redundant parsing across middlewares and handlers.

---

### Usage in Code

```python
from fastapi import FastAPI, Request

@app.post("/api/user/update")
async def update_user(request: Request):
    # 1. Retrieve the entire parsed body dictionary
    data = await req.b()

    # 2. Retrieve a specific body parameter with default fallback
    name = await req.b("name", default="Anonymous")
    email = await req.b("email")

    # 3. Retrieve request header
    auth_header = await req.h("authorization")
    api_key = await req.h("x-api-key")

    # 4. Retrieve query parameters (?page=1&limit=20)
    page = await req.q("page", default="1")
    limit = await req.q("limit", default="20")

    return res.s("Data retrieved successfully", {"name": name, "email": email, "page": page})
```

---

## 9. Security & Cryptography Utilities

High-security, production-hardened cryptographic utilities globally available across the application.

---

### 9.1 AES-256-GCM Encryption (`aes`)

Provides military-grade authenticated symmetric encryption using **AES-256-GCM** with HKDF SHA-256 key derivation and fresh 12-byte random nonces per operation.

#### Key Features
- **Global Availability:** Registered in `builtins.aes`.
- **Zero Configuration:** Automatically derives a 256-bit cryptographically strong key via HKDF from any secret passphrase or byte sequence.
- **Integrity Protection:** Embeds AEAD authentication tag to detect any tampering or bit-flipping attacks.
- **Direct Object Support:** Automatically serializes dictionaries, lists, strings, and integers to JSON before encryption.

#### Usage Example

```python
# Secret key (can be any passphrase or from env)
secret_key = env("ENCRYPTION_KEY", "super-secret-passphrase-32-bytes-long")

# 1. Encrypt a dictionary or sensitive payload
sensitive_data = {"user_id": 101, "card_token": "tok_9918237"}
encrypted_token = aes.e(sensitive_data, secret_key)
# Output: Base64 string containing [12-byte IV + Ciphertext + 16-byte Tag]

# 2. Decrypt back to a dictionary (as_json=True)
decrypted_data = aes.d(encrypted_token, secret_key, as_json=True)
print(decrypted_data["card_token"])  # tok_9918237

# 3. Decrypt plain text (as_json=False)
plain_text = aes.d(encrypted_token, secret_key)
```

---

### 9.2 Base64 Helper (`base`)

A fast Base64 encoding and decoding utility with automatic JSON serialization and UTF-8 handling.

#### Key Features
- **Global Availability:** Registered in `builtins.base`.
- **Native Data Support:** Encodes dictionaries, lists, strings, and raw bytes directly without manual JSON conversion.

#### Usage Example

```python
# 1. Encode dictionary or string to Base64
payload = {"status": "active", "tier": "gold"}
encoded = base.e(payload)

# 2. Decode Base64 string back to JSON dictionary
decoded_dict = base.d(encoded, as_json=True)

# 3. Decode plain string
text_encoded = base.e("Hello World")
decoded_str = base.d(text_encoded)
```

---

### 9.3 OWASP Password Hashing (`password`)

Secure password hashing and verification using the **Argon2id** algorithm (RFC 9106), optimized to resist GPU/ASIC brute-force and side-channel attacks.

#### Key Features
- **Global Availability:** Registered in `builtins.password`.
- **OWASP Recommended Parameters:** `memory_cost=65536` (64 MiB), `time_cost=4`, `parallelism=1`.
- **DoS Protection:** Enforces a 4096-byte limit on passwords to prevent CPU exhaustion.
- **Constant-Time Verification:** Protects against timing side-channel attacks.

#### Usage Example

```python
# 1. Hash a user password during registration
user_password = "UserSecurePassword@2026"
password_hash = password.hash(user_password)
# Output: $argon2id$v=19$m=65536,t=4,p=1$...

# 2. Verify password during login (returns True / False)
is_valid = password.verify("UserSecurePassword@2026", password_hash)
if not is_valid:
    return res.e("Invalid credentials", 401)
```

---

### 9.4 Stateless Encrypted Token Manager (`token`)

A secure, tamper-proof alternative to standard JWTs, using AES-256-GCM encrypted payloads with optional Client IP and Device Fingerprint binding.

#### Key Features
- **Global Availability:** Registered in `builtins.token` (`TokenManager`).
- **Encrypted Payload:** Unlike standard JWTs where data is publicly visible in Base64, token contents are fully encrypted with AES-256-GCM.
- **Device & IP Fingerprint Binding:** Optionally binds the token to the client's IP and User-Agent device signal to prevent token hijacking.
- **Key Rotation Support:** Multi-key dictionary support using Key IDs (`kid`).

#### Configuration Setup (`.env`)

```env
# Minimum 32-character encryption key(s)
TOKEN_MANAGER_KEYS='{"v1": "a_secure_token_secret_key_minimum_32_chars_12345"}'
```

#### Usage Example

```python
# 1. Generate an encrypted session token
auth_token = token.generate(
    usecase="auth_session",
    data={"user_id": 101, "role": "admin"},
    expiry="2h",           # Supports "15m", "1h", "7d", "30d"
    use_ip=True,           # Binds token to client IP
    use_device=True        # Binds token to client device/browser
)

if auth_token["status"]:
    token_string = auth_token["token"]
    # Send token_string to client in Authorization header or cookie

# 2. Verify and decode incoming token
result = token.verify(token_string, expected_usecase="auth_session")

if not result["status"]:
    # Returns specific error: "token_expired", "invalid_token", "ip_mismatch", etc.
    return res.e(f"Authentication failed: {result.get('error')}", 401)

# Successfully authenticated
user_data = result["data"]  # {"user_id": 101, "role": "admin"}
user_id = user_data["user_id"]
```

#### Random Unique Token Generator (32 / 64 Characters)

OS-level CSPRNG (`secrets` module) ka use karke 100% collision-free, globally unique opaque tokens generate karne ke liye:

```python
# 1. Direct Call (Sabse aasan tarika: 32 ya 64 characters)
t32 = token(32)             # e.g. "395ebe23cdb5504f11feba95fd31f6ac" (32 chars)
t64 = token(64)             # e.g. "388b95de0f7ff9210da984f1eb88e5f0..." (64 chars)

# 2. .random() Method (Hex, URL-safe ya Alphanumeric)
token_32 = token.random(32)           # Default Hex format (32 chars)
token_64 = token.random(64)           # Default Hex format (64 chars)

# 3. .hex() Shortcuts
hex_32 = token.hex(32)
hex_64 = token.hex(64)

# 4. URL-Safe Format (Verification Links, Password Reset, API Keys ke liye best)
url_32 = token.urlsafe(32)            # "bGyBIBjQMALMZ7uSSMw0fEkfj3jdQQJM" (32 chars)
url_64 = token.urlsafe(64)            # 64 chars URL-safe (A-Za-z0-9-_)

# 5. Alphanumeric Only (Bina special character ke)
clean_32 = token.random(32, mode="alphanumeric")
```

---

### 9.5 Ed25519 Digital Signature (`dsc`, `dscToken`, `dscVerify`)

Provides high-speed, cryptographically secure digital signatures using **Ed25519** elliptic curves for microservice communication, webhook signing, and tamper-proof data verification.

#### Key Features
- **Global Availability:** Registered in `builtins.dsc`, `builtins.dscToken`, and `builtins.dscVerify`.
- **Fast & Modern:** Uses Ed25519 asymmetric cryptography (faster and more secure than legacy RSA).
- **Canonical Serialization:** Ensures deterministic JSON serialization (`sort_keys=True`) before signing.

#### Usage Example

```python
# 1. Generate Keypair (creates private.pem and public.pem in directory)
dscToken("storage/keys/dsc")

# 2. Sign a payload using the private key
order_data = {"order_id": "ORD-5501", "amount": 1500.0, "status": "approved"}
signed_package = dsc(order_data, "storage/keys/dsc/private.pem")
# Output:
# {
#   "data": "<base64_canonical_json>",
#   "token": "<base64_ed25519_signature>"
# }

# 3. Verify signature using public key (returns True / False)
is_authentic = dscVerify(
    order_data,
    signed_package["token"],
    "storage/keys/dsc/public.pem"
)

if not is_authentic:
    return res.e("Digital signature verification failed! Data altered.", 403)
```

---

## 10. Anti-Exploit String Validator (`GuardString`)

The `GuardString` utility in `App/src/Validator` sanitizes and validates untrusted user input strings against malicious exploits, homoglyphs, control characters, and Unicode attacks.

### Key Features
- **Global Availability:** Registered in `builtins.GuardString`, `builtins.validator`, and `builtins.Validator`.
- **Control Character Detection:** Blocks invisible ASCII and Unicode control codes (`0x00`-`0x1F`, `0x7F`, etc.).
- **Invisible & Zero-Width Characters:** Blocks zero-width spaces (`\u200B`), soft hyphens, directional overrides, and hidden bypass characters.
- **Homoglyph & Mixed-Script Defense:** Blocks dangerous mixed alphabet combinations (such as Cyrillic/Greek characters mixed with Latin) to prevent IDN spoofing and impersonation attacks.
- **Repetition & Size Limits:** Rejects strings exceeding 64KB or characters repeated 100+ times to prevent CPU/memory ReDoS.
- **NFC Unicode Normalization:** Normalizes input characters to standard Unicode Normalization Form C.

---

### Usage in Code

```python
# 1. Strict string validation (Default)
result = GuardString.str(untrusted_input)

if not result["valid"]:
    error_info = result["errors"][0]
    return res.e(f"Validation failed: {error_info['message']}", 422)

clean_string = result["value"]

# 2. Relaxed validation (strict=False)
# Disables control/invisible character checks while keeping 64KB size limit & trim
relaxed = GuardString.str(user_bio, strict=False)

# 3. Disable auto-trimming (trim=False)
exact_string = GuardString.str(raw_code, trim=False)
```

#### Return Format:
- **On Success:**
  ```json
  {
    "valid": true,
    "value": "Clean string value"
  }
  ```
- **On Failure:**
  ```json
  {
    "valid": false,
    "errors": [
      {
        "code": "CONTROL_CHARACTERS",
        "message": "Control characters are not allowed."
      }
    ]
  }
  ```

---

## 11. Main API Entry Gate (`entry`)

The `entry` utility provides a centralized API Gateway and routing entrypoint in `App/entry.py`. All incoming API requests flow through this gate before reaching individual endpoints, modules, or controllers.

### Key Features
- **Global Availability:** Registered in `builtins.entry` and `App.app.entry`.
- **Zero-Boilerplate Mounting:** Mount the entire API gateway onto FastAPI with a single clean call in `main.py`: `entry(app)`.
- **Pre-Flight Gatekeeper:** Automatically verifies environment readiness, captures client metadata (`user_info`), and logs request paths.
- **Unified Prefixing:** By default prefixes all attached API endpoints with `/api` (customizable).
- **Sub-Router Modularization:** Attach sub-routers (e.g. `/v1`, `/auth`, `/users`) using `entry.include_router(...)`.

---

### Usage in Code

#### 1. In `main.py` (Custom Entry Gate with Request Metadata & Checks):
```python
from fastapi import FastAPI, Request
import App.app

app = FastAPI(lifespan=App.app.lifespan)
App.app.init(app)

# Main API Entry Gate:
# Yahan se aap IP, Browser, OS, Body, Headers check kar sakte hain,
# ya SQL / maintenance toggle laga sakte hain (bina automatic background logging ke):
@entry(app)
async def gate(request: Request):
    ip = user_info.ip(request)
    browser = user_info.browser()
    os_name = user_info.os()
    data = await req.b()
    auth_header = await req.h()

    maintenance = False
    if maintenance:
        return res.e("API is currently unavailable", 422)
    return True

if __name__ == "__main__":
    App.app.run()
```

#### 2. Defining or Mounting Sub-Routes via `entry`:
```python
from fastapi import APIRouter

# Option A: Direct route on entry
@entry.get("/status")
async def api_status():
    return res.s("API is operational")

# Option B: Attach a modular feature router (e.g. v1 / auth)
auth_router = APIRouter(prefix="/auth")

@auth_router.post("/login")
async def login():
    return res.s("Login successful")

# Include into the entry gate:
entry.include_router(auth_router)
# Endpoint is now active at: POST /api/auth/login
```

#### 3. Default Gateway Health Endpoint:
Visiting `GET /api` returns the gateway health status:
```json
{
  "status": true,
  "status_code": 200,
  "message": "API Entry Gate Active",
  "data": {
    "gateway": "online",
    "prefix": "/api"
  }
}
```

---

## 12. Asynchronous Redis Client (`redis`)

The `redis` utility in `App/database/redis.py` provides high-performance Redis caching, session storage, and queue management with multi-database support and auto-JSON serialization.

### Key Features
- **Global Availability:** Registered in `builtins.redis`, directly accessible anywhere without importing.
- **Dual Execution Mode (`_FlexResult`):** Can be executed **with `await`** in async routes OR **without `await`** in synchronous contexts (tasks are automatically scheduled/resolved).
- **Multi-Database Support:** Direct database targeting via parameter `db=1`, `db=2`, etc. (defaults to `REDIS_DB=0`).
- **Auto JSON Serialization:** Directly pass Python dictionaries and lists to `set` and `lpush`; retrieve parsed objects using `as_json=True`.
- **TTL Support:** Set key expiration directly via `ttl=seconds`.

---

### Configuration Setup (`.env`)

```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
# Or single connection URL:
# REDIS_URL=redis://:password@127.0.0.1:6379/0
```

---

### Usage in Code

#### 1. Calling Without `await` (Sync / Background scheduling):
```python
# Default DB (REDIS_DB=0) mein TTL ke saath set
redis.set("otp:9876543210", "482910", ttl=120)

# Specific DB (db=1) mein TTL ke saath set
redis.set("otp:9876543210", "482910", ttl=120, db=1)

# Dict / list bhi directly pass kar sakte hain (auto JSON)
redis.set("user:101", {"name": "Rohit", "city": "Kanpur"}, ttl=300, db=2)

# List mein items push karna (ttl aur db ke saath)
redis.lpush("events:user:101", "login", "viewed_order", ttl=600)
redis.lpush("jobs:email", {"to": "a@example.com", "tpl": "welcome"}, ttl=900, db=1)

# Key delete karna (default DB ya specific DB)
redis.delete("otp:9876543210")
redis.delete("otp:9876543210", db=1)

# Health Check bina await ke
redis.isConnected()
redis.isConnected(db=1)
```

---

#### 2. Calling With `await` (Async Routes):
```python
# Default DB (REDIS_DB=0) mein TTL ke saath set
await redis.set("otp:9876543210", "482910", ttl=120)

# Specific DB (db=1) mein TTL ke saath set
await redis.set("otp:9876543210", "482910", ttl=120, db=1)

# Dict / list bhi directly pass kar sakte hain (auto JSON)
await redis.set("user:101", {"name": "Rohit", "city": "Kanpur"}, ttl=300, db=2)

# Retrieve data (as_json=True for dict/list)
user = await redis.get("user:101", as_json=True, db=2)

# List mein items push karna (ttl aur db ke saath)
await redis.lpush("events:user:101", "login", "viewed_order", ttl=600)
await redis.lpush("jobs:email", {"to": "a@example.com", "tpl": "welcome"}, ttl=900, db=1)

# List se items retrieve karna
events = await redis.lrange("events:user:101", 0, -1)

# Key delete karna (default DB ya specific DB)
await redis.delete("otp:9876543210")
await redis.delete("otp:9876543210", db=1)

# Health Check await ke saath (result boolean return hota hai)
connected = await redis.isConnected()
connected_db1 = await redis.isConnected(db=1)
```

---

## 13. CORS Configuration (`cors`)

The CORS utility in `App/security/cors.py` configures Cross-Origin Resource Sharing on FastAPI to control which frontend origins, headers, and HTTP methods can access your API.

### Key Features
- **Global Availability:** Registered in `builtins.cors`.
- **Automatic Initialization:** Automatically configured during `App.app.init(app)` using `.env` settings.
- **Customizable:** Can be invoked directly with custom origins, headers, and methods: `cors(app, origins=["https://myfrontend.com"])`.
- **Configurable Credentials & Max Age:** Supports `allow_credentials=True` and preflight cache duration.

---

### Configuration Setup (`.env`)

Add the following 5 settings to your `.env` file:

```env
# 1. Allowed Origins (Domain whitelist)
CORS_ORIGINS=*

# 2. Allowed Headers
CORS_HEADERS=*

# 3. Allowed HTTP Methods
CORS_METHODS=*

# 4. Allow Cookies / Authorization Headers
CORS_CREDENTIALS=true

# 5. Preflight Cache Duration (in seconds)
CORS_MAX_AGE=600
```

---

### How to Configure Each Setting (`.env` Guide)

| Setting Key | Default | Example Value | Description & How to Use |
| :--- | :--- | :--- | :--- |
| **`CORS_ORIGINS`** | `*` | `*`<br>or<br>`https://frontend.com,https://admin.site.com` | **Frontend Domains:** Defines which origins can make requests to your API.<br>• Use `*` to allow all origins (ideal for development or public APIs).<br>• In production, list specific allowed domains separated by commas. |
| **`CORS_HEADERS`** | `*` | `*`<br>or<br>`Authorization,Content-Type,Accept` | **Request Headers:** Defines which custom HTTP headers clients are allowed to send.<br>• Use `*` to accept all request headers.<br>• In strict production setups, list only headers used by your frontend. |
| **`CORS_METHODS`** | `*` | `*`<br>or<br>`GET,POST,PUT,DELETE,OPTIONS` | **HTTP Methods:** Whitelist allowed HTTP verbs.<br>• Use `*` to accept all verbs (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD).<br>• Or restrict to specific methods separated by commas. |
| **`CORS_CREDENTIALS`** | `true` | `true` or `false` | **Cookies & Auth Headers:** Whether browsers are allowed to expose responses to frontend JavaScript when credentials (cookies, HTTP auth) are sent.<br>• Set to `true` if your frontend sends cookies or auth headers.<br>• Set to `false` for public stateless APIs. |
| **`CORS_MAX_AGE`** | `600` | `600` or `3600` | **Preflight Cache (Seconds):** How long (in seconds) the browser can cache the preflight `OPTIONS` response.<br>• `600` = 10 minutes.<br>• Eliminates redundant `OPTIONS` requests on every API call, speeding up response times. |

---

### Environment Setup Examples

#### 1. Development Environment (Permissive)
```env
CORS_ORIGINS=*
CORS_HEADERS=*
CORS_METHODS=*
CORS_CREDENTIALS=true
CORS_MAX_AGE=600
```

#### 2. Production Environment (Strict Whitelist)
```env
CORS_ORIGINS=https://myfrontend.com,https://admin.myfrontend.com
CORS_HEADERS=Authorization,Content-Type,Accept,X-Requested-With
CORS_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
CORS_CREDENTIALS=true
CORS_MAX_AGE=3600
```

---

### Usage in Code

#### 1. Automatic (Default via `App.app.init`):
CORS is automatically loaded from `.env` when initializing the application:
```python
import App.app

App.app.init(app)  # CORS middleware is applied automatically from .env
```

#### 2. Explicit or Custom Origins (`cors`):
```python
# Custom origin configuration:
cors(
    app,
    origins=["https://myfrontend.com", "https://admin.myfrontend.com"],
    headers=["Authorization", "Content-Type", "Accept"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    credentials=True,
    max_age=3600,
)
```

---

## 14. Complete API Endpoint Guide (Step-by-Step with SlowAPI)

This section demonstrates how to create a complete, production-ready API endpoint in the `routes/` directory using all framework utilities:
- **`APIRouter`** (FastAPI route controller)
- **`slowapi`** (Official Rate Limiting per IP)
- **`@body.limit`** (Payload size restriction)
- **`req.b()` / `req.h()`** (Request body & header accessor)
- **`res.s()` / `res.e()`** (Standardized responses)
- **Automatic Routing** (No manual imports required in `main.py`)

---

### 1. Folder Structure & Automatic URL Routing

Any `.py` file placed inside the `routes/` directory is automatically discovered and mounted under the `/api` entry gateway:

| File Location | Endpoint Prefix | Example Full URL |
| :--- | :--- | :--- |
| `routes/auth.py` | `/auth` | `POST /api/auth/login` |
| `routes/user/login.py` | `/user/login` | `POST /api/user/login` |
| `routes/user/register.py` | `/user/register` | `POST /api/user/register` |

You **never need to modify `main.py`** to add or import new route files.

---

### 2. Full Working Example: `routes/auth.py`

Create or edit your route file in `routes/auth.py`:

```python
from fastapi import APIRouter, Request

# Create FastAPI Router
router = APIRouter()


# ==============================================================================
# 1. Login Endpoint with Rate Limiting & Payload Guards
# ==============================================================================
@router.post("/login")
@limiter.limit("5/minute")        # SlowAPI: Maximum 5 attempts per minute per IP
@body.limit("100KB")             # Body Limit: Maximum 100 KB payload size
async def auth_login(request: Request):
    """
    User login endpoint.
    Auto URL: POST /api/auth/login
    """
    # 1. Extract JSON / Form Body
    data = await req.b(request)
    email = data.get("email")
    raw_password = data.get("password")

    # 2. Input Validation
    if not email or not raw_password:
        return res.e("Email and password are required", 400)

    # 3. Sanitization with GuardString (Anti-Exploit)
    clean_email = GuardString(email).trim().lower().get()

    # 4. Query User from Database (SQLite / Postgres / MySQL)
    query = "SELECT id, email, password_hash, status FROM users WHERE email = :email LIMIT 1"
    users = DB.raw(query, {"email": clean_email})

    if not users:
        return res.e("Invalid email or password", 401)

    user = users[0]

    # 5. Verify Password with Argon2
    if not password.verify(raw_password, user["password_hash"]):
        return res.e("Invalid email or password", 401)

    # 6. Generate Secure JWT Token
    jwt_token = token.create({"sub": str(user["id"]), "email": clean_email})

    # 7. Success Response
    return res.s(
        "Login successful",
        {
            "token": jwt_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
            },
        },
    )


# ==============================================================================
# 2. Registration Endpoint
# ==============================================================================
@router.post("/register")
@limiter.limit("3/minute")        # SlowAPI: Maximum 3 registrations per minute per IP
@body.limit("100KB")             # Body Limit: Maximum 100 KB payload size
async def auth_register(request: Request):
    """
    User registration endpoint.
    Auto URL: POST /api/auth/register
    """
    data = await req.b(request)
    email = data.get("email")
    raw_password = data.get("password")

    if not email or not raw_password:
        return res.e("Email and password are required", 400)

    clean_email = GuardString(email).trim().lower().get()

    # Hash Password with Argon2id
    hashed_pwd = password.hash(raw_password)

    # Insert into Database
    insert_sql = "INSERT INTO users (email, password_hash) VALUES (:email, :pwd)"
    DB.raw(insert_sql, {"email": clean_email, "pwd": hashed_pwd})

    return res.s("Registration successful", {"email": clean_email})
```

---

### 3. How Rate Limiting Works (`slowapi`)

SlowAPI rate limiting pure project me centralized config ke sath use hoti hai:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

# Standard Official SlowAPI Rate Limiter
limiter = Limiter(key_func=get_remote_address)
```

- **Builtin Availability:** `limiter` instance project ke `builtins` me globally registered hai, isliye kisi bhi route file me bina alag se import kiye direct `@limiter.limit(...)` decorator use kiya ja sakta hai.
- **Decorator Usage:** `@limiter.limit("3/minute")` ya `@limiter.limit("100/hour")` lagakar IP-based rate limiting enforce hoti hai.
- **Request Parameter Requirement:** SlowAPI ke decorator ko client IP extract karne ke liye endpoint function me `request: Request` parameter ka hona compulsory hai (`async def endpoint_name(request: Request):`).
- **Professional 429 Response:** Jab koi client limit exceed karta hai, toh centralized exception handler automatically HTTP 429 response return karta hai:
  ```json
  {
    "status": false,
    "status_code": 429,
    "message": "Too many requests. You have exceeded your rate limit. Please try again later.",
    "data": []
  }
  ```

---

## 15. Zero-Dependency HTTP Client (`http`)

The framework includes a built-in, lightweight HTTP client (`http`) powered entirely by Python's native standard library (`urllib.request`). It requires **zero external third-party dependencies** (no `requests` or external packages needed) while providing a modern, developer-friendly API.

### Key Features
- **Global Availability:** Registered in `builtins.http`, accessible everywhere across your routes and services without `import`.
- **Zero External Dependencies:** Built 100% on Python's native `urllib` standard library.
- **Smart JSON Handling:** Passing a Python dictionary or list automatically serializes it to JSON and attaches the `Content-Type: application/json` header.
- **Default Safe Timeout:** Comes with a built-in 10-second timeout to prevent third-party API freezes from hanging your server.
- **Crash-Free Error Handling:** 4xx and 5xx HTTP responses do not raise unhandled exceptions; they safely return an `HttpResponse` object with `status_code`, `ok=False`, and error details.
- **Direct Dict-Like Indexing:** If the response is a JSON object, access fields directly via `res["key"]` or `res.get("key")`.

---

### Usage in Code

#### 1. HTTP GET Request
```python
# 1. Simple GET
res = http.get("https://api.example.com/users")

# 2. GET with Query Parameters & Custom Headers
res = http.get(
    "https://api.example.com/search",
    params={"query": "fastapi", "page": 1},
    headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
)

if res.ok:
    print("Status:", res.status_code)        # 200
    print("User Name:", res["data"]["name"]) # Direct dict indexing
    print("Full JSON:", res.json())          # Parsed dictionary / list
```

---

#### 2. HTTP POST Request
```python
# 1. Direct JSON Payload (Dict pass karte hi auto-JSON ban jata hai)
user_payload = {
    "name": "Satyam",
    "email": "satyam@example.com",
    "role": "admin"
}

res = http.post("https://api.example.com/users", user_payload)

# 2. POST with Custom Headers (e.g. Bearer Token)
res = http.post(
    "https://api.example.com/secure",
    {"key": "value"},
    headers={"Authorization": "Bearer xyz"}
)

if res:  # Truthy if status is 2xx
    print("Created successfully:", res["id"])
else:
    print("Request failed with status:", res.status_code, "Error:", res.error)
```

---

#### 3. PUT, PATCH, and DELETE Requests
```python
# Update resource (PUT)
res = http.put("https://api.example.com/users/101", {"name": "New Name"})

# Partial update (PATCH)
res = http.patch("https://api.example.com/users/101", {"status": "active"})

# Delete resource (DELETE)
res = http.delete("https://api.example.com/users/101")
```

---

#### 4. Handling Responses (`HttpResponse` Properties)

| Property / Method | Description | Example |
| :--- | :--- | :--- |
| `res.status_code` | HTTP Status Code integer | `200`, `404`, `500` |
| `res.ok` | `True` for 2xx status codes, otherwise `False` | `if res.ok:` |
| `res.json()` | Parsed JSON body (dict or list) | `data = res.json()` |
| `res.text` | Raw response decoded as UTF-8 string | `html = res.text` |
| `res.headers` | Response headers dictionary | `content_type = res.headers.get("Content-Type")` |
| `res.error` | Human-readable error message if request failed | `"HTTP 404: Not Found"` |
| `res["field"]` | Direct subscription access for JSON bodies | `user_id = res["id"]` |
| `res.get("field")` | Safe dictionary `.get()` fallback | `token = res.get("token", None)` |

---

## How to Run the Project (Project Run Kaise Karein)

### Step 1: Environment Setup (.env)
Project root par `.env` file verify karein. Agar `.env` nahi hai toh `.env.example` se copy karein:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

### Step 2: Virtual Environment Activate Karein
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

### Step 3: Dependencies Install Karein (First Time Setup)
```bash
pip install -r requirements.txt
```

### Step 4: Server Run Karein
Aap server ko do tarike se run kar sakte hain:

#### Option A: Direct Python (Recommended)
```bash
python main.py
```
Isme automatically:
- `.env` configurations load hongi.
- Uvicorn server `127.0.0.1:8000` par start ho jayega.
- Auto-reload enable rahega (`APP_RELOAD=true`).
- Startup par automatically `__pycache__` clean hoga.

#### Option B: Direct Uvicorn
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

### Important URLs & Endpoints

| Resource | URL | Description |
| :--- | :--- | :--- |
| **Root Health Probe** | `http://127.0.0.1:8000/` | Base server running probe |
| **API Entry Gateway** | `http://127.0.0.1:8000/api` | Centralized API entry gate |
| **Interactive Docs (Swagger)** | `http://127.0.0.1:8000/docs` | Swagger UI (`DOCS=true` hone par) |
| **Alternative Docs (ReDoc)** | `http://127.0.0.1:8000/redoc` | ReDoc API documentation |
| **Database Web Admin** | `http://127.0.0.1:8000/db` | SQLite web database viewer |
