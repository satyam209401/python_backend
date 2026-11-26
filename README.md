<div align="center">

# ⚡ FastAPI Enterprise Backend Architecture

**A modular, high-performance, and military-grade secure asynchronous backend framework for Python.**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Cryptography](https://img.shields.io/badge/Security-AES--256--GCM%20%7C%20Argon2id-red.svg?style=for-the-badge&logo=securityscorecard&logoColor=white)](https://cryptography.io)
[![Databases](https://img.shields.io/badge/Databases-MySQL%20%7C%20SQLite%20%7C%20Redis-orange.svg?style=for-the-badge&logo=mysql&logoColor=white)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

[Key Features](#-key-features) • [Project Structure](#-project-structure) • [Installation & Setup](#-installation--setup) • [Core Utilities](#-core-utilities) • [Security & Cryptography](#-security--cryptography) • [Database Drivers](#-database-drivers) • [API Documentation](#-api-documentation)

---

</div>

## 📌 Overview

This repository provides an enterprise-ready, production-hardened foundation for modern APIs. It eliminates repetitive boilerplate by providing **Zero-Import Global Injections**, military-grade authenticated encryption (**AES-256-GCM**), stateless yet revokable encrypted session tokens (**TokenManager**), OWASP-compliant password hashing (**Argon2id**), anti-exploit Unicode & homoglyph sanitization (**GuardString**), asymmetric digital signatures (**Ed25519 DSC**), and native multi-database connectors (**MySQL, SQLite, Redis**).

---

## 🚀 Key Features

* **⚡ Modern Asynchronous Core:** Built on top of **FastAPI**, **Starlette**, and **Uvicorn** with automatic OpenAPI (Swagger UI) and ReDoc generation.
* **📁 Scalable Versioned Routing:** Clean directory-based version routing (`/v1` and `/v2`) for seamless API evolution.
* **🌐 Zero-Import Global Injections (`builtins`):** High-frequency utilities are globally accessible across all files without importing:
  * `res` — Standardized API response builder (`res.s()` for success, `res.e()` for errors).
  * `env` — Resilient environment variable loader with production path detection.
  * `req` — Universal request accessor (`req.b()` body, `req.h()` headers, `req.q()` query params).
  * `token` — Military-grade encrypted JWT alternative with device and IP fingerprint binding.
  * `password` — Argon2id OWASP password hashing and constant-time verification.
  * `GuardString` — Anti-exploit string sanitizer protecting against control codes and homoglyphs.
  * `aes` — Authenticated AES-256-GCM encryption with HKDF key derivation.
  * `dsc` / `dscToken` / `dscVerify` — Ed25519 asymmetric cryptographic signing and verification.
  * `base` — Fast Base64 encoder and decoder with native JSON object support.
  * `body` — Request payload size limiter protecting endpoints against Memory DoS (`@body.limit("2MB")`).
  * `user_info` — Cloudflare-aware Client IP, OS, Browser, and Device detection.
  * `redis` — Asynchronous Redis client with auto JSON handling and connection lifecycle management.
  * `sqlite` — Thread-safe asynchronous SQLite driver running in high-speed WAL mode.
  * `DB` / `MySQLDB` — Multi-database MySQL manager with connection pooling and transactions.
  * `pg` — Multi-database PostgreSQL manager with connection pooling and transactions.
* **🛡️ Hardened Network Security:** Configurable CORS middleware with dynamic origins and header controls via `.env`.

---

## 📂 Project Structure

```text
py_backend/
├── App/
│   ├── app.py                  # Global bootstrap & builtins registration
│   ├── database/               # Database connectors & connection managers
│   │   ├── mysql.py            # MySQL manager & transaction runner (MySQLDB, DB)
│   │   ├── pg.py               # PostgreSQL manager & transaction runner (pg)
│   │   ├── redis.py            # Async Redis manager with multi-db support (redis)
│   │   └── sqlite.py           # Async SQLite manager with WAL mode (sqlite)
│   ├── exception_handler/      # Centralized modular exception handlers
│   │   ├── http.py             # HTTP status exceptions
│   │   ├── rate_limit.py       # SlowAPI rate limit handlers
│   │   ├── server.py           # Internal 500 server crash concealment
│   │   └── validation.py       # Pydantic & request validation errors
│   ├── security/               # Cryptographic primitives & security utilities
│   │   ├── aes/                # Authenticated AES-256-GCM (enc.py, dec.py)
│   │   ├── base64/             # Base64 encoder & decoder (enc.py, des.py)
│   │   ├── password.py         # Argon2id password hashing (Password: hash, verify)
│   │   └── token.py            # Encrypted Token Manager (TokenManager, token)
│   └── src/
│       ├── Validator/
│       │   └── str.py          # Anti-exploit string validator (GuardString)
│       ├── dsc/
│       │   └── dsc.py          # Ed25519 digital signatures (dscToken, dsc, dscVerify)
│       └── utils/
│           ├── body.py         # Request payload size limiter (body.limit)
│           ├── log.py          # Auto-caller file routing logger (log)
│           ├── req.py          # Context-aware request helper (b, h, q)
│           ├── response.py     # Unified JSON response builder (Response: s, e)
│           └── user_info.py    # Client device & IP detector (user_info)
├── routes/
│   ├── v1/                     # Version 1 API Endpoints
│   │   ├── admin/              # Administrative endpoints (dashboard, payment, user)
│   │   ├── auth/               # Authentication endpoints (login, register)
│   │   └── booking/            # Booking endpoints (plot)
│   └── v2/                     # Version 2 API Endpoints (extensible)
├── .env.example                # Sample environment configuration template
├── env.py                      # Multi-environment detection & loader
├── main.py                     # Application entry point & FastAPI instance
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository & Navigate
Clone the codebase from GitHub and enter the project directory:
```bash
# Clone the repository
git clone https://github.com/satyam209401/python_backend.git

# Navigate into the project folder (Crucial Step!)
cd python_backend
```

### 2. Set Up Virtual Environment
Create and activate an isolated Python virtual environment:

#### Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
> **Tip:** If PowerShell gives a script execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

#### Windows (Command Prompt - CMD):
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

#### Linux / macOS (Bash / Zsh):
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Ensure `pip` is up to date, then install all required packages:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
Copy `.env.example` to create your active `.env` configuration file:

#### Windows (PowerShell):
```powershell
Copy-Item .env.example .env
# or
cp .env.example .env
```

#### Windows (CMD):
```cmd
copy .env.example .env
```

#### Linux / macOS:
```bash
cp .env.example .env
```

#### Accessing Environment Variables in Code:
`env` is globally accessible anywhere without importing:
```python
port = env("PORT", "8000")
secret_key = env("SECRET_KEY")
```

### 5. Run the Application

#### Development Mode (Auto-Reload):
Always use `python -m uvicorn` to guarantee the virtual environment's binary is executed cleanly:
```bash
python -m uvicorn main:app --reload
```
The API server will start at: `http://127.0.0.1:8000`
* **Swagger UI Documentation:** `http://127.0.0.1:8000/docs`
* **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

#### Production Mode:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

### 💡 Common Setup Troubleshooting

| Issue / Error | Cause | Solution |
| :--- | :--- | :--- |
| `'uvicorn' is not recognized` | Virtual environment is not activated or `requirements.txt` was not installed. | Activate `venv` and run `pip install -r requirements.txt`, then run with `python -m uvicorn main:app --reload`. |
| `Cannot find path '.env.example'` | Terminal is not inside the project directory. | Run `cd python_backend` first, ensure `ls` or `dir` shows `.env.example`, then copy. |
| `PSSecurityException / Script Execution` | PowerShell restricts unsigned script execution. | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` in PowerShell. |

---

## 🌐 Core Utilities

### 1. Standard Response Builder (`res`)
Ensures uniform API responses across the entire application:

#### Success Response:
```python
return res.s("User fetched successfully", {"user_id": 101, "name": "Rahul"})
```
```json
{
  "status": true,
  "status_code": 200,
  "message": "User fetched successfully",
  "data": {
    "user_id": 101,
    "name": "Rahul"
  }
}
```

#### Error Response:
```python
return res.e("Username is required", 400)
```
```json
{
  "status": false,
  "status_code": 400,
  "message": "Username is required",
  "data": []
}
```

---

### 2. Universal Request Accessor (`req`)
Extracts request body, headers, or query parameters asynchronously without passing parameters through multiple layers:

#### Body Data (`req.b`):
```python
# Get entire body as dict (JSON or Form data)
body = await req.b()

# Get a specific key from body
username = await req.b("username")
```

#### Request Headers (`req.h`):
```python
# Get all headers as dict
headers = await req.h()

# Get a specific header value (case-insensitive)
token = await req.h("session_token")
```

#### Query Parameters (`req.q`):
```python
# Get all query parameters as dict
query = await req.q()

# Get a specific query parameter
page = await req.q("page")
```

---

### 3. Smart File Logger (`log`)
Automatically identifies the calling file and writes formatted logs to `logs/<caller_file>.log`:

```python
# 1) Auto-routed string log (saves to logs/<calling_file>.log)
log("User registered successfully")

# 2) Structured JSON data log
log({"user_id": 101, "action": "login", "status": "success"})

# 3) Custom destination path
log("Payment transaction complete", "logs/payments.log")
```

---

### 4. Client & Device Detection (`user_info`)
Detects client IP (aware of Cloudflare `CF-Connecting-IP` and trusted proxies) and parses client device information:

```python
# 1) Get single property
ip = user_info.info("ip")           # Client IP (Proxy & Cloudflare aware)
browser = user_info.info("browser") # Chrome, Firefox, Safari, Edge, Opera
os_name = user_info.info("os")      # Windows, Android, iOS, macOS, Linux
device = user_info.info("device")   # Desktop, Mobile, Tablet

# 2) Get all client info as dictionary
client_details = user_info.info()
```

---

### 5. Request Payload Limiter (`body`)
Protects endpoints against memory exhaustion and large payload DoS attacks (`B`, `KB`, `MB`, `GB` supported):

```python
@router.post("/upload")
@body.limit("2MB")
async def upload_file():
    # If request body > 2MB, automatically raises 413:
    # {"status": false, "status_code": 413, "message": "Request payload too large.", "data": []}
    data = await req.b()
    return res.s("Uploaded successfully", {"size": len(str(data))})
```

---

## 🔐 Security & Cryptography

### 6. Anti-Exploit String Sanitizer (`GuardString`)
Sanitizes and validates untrusted strings against Unicode exploits, control characters, invisible zero-width characters, excessive repetition, and homoglyph attacks:

```python
# Validate string input
result = GuardString.str(user_input, strict=True, trim=True)

if not result["valid"]:
    # Returns specific error code and message
    return res.e(result["errors"][0]["message"], 400)

clean_value = result["value"]
```

#### Success Output:
```json
{
  "valid": true,
  "value": "Clean string value"
}
```

#### Failure Output:
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

### 7. Encrypted Token Manager (`token`)
An ultra-secure, military-grade replacement for standard JWT. Payloads are fully encrypted using **AES-256-GCM**, supporting active key rotation (`kid`), human-readable TTLs, and optional hardware/network security binding:

#### 1) Configuration (`.env`):
```env
TOKEN_MANAGER_KEYS={"v1":"swarg_marg_token_secret_key_32_chars_min_123456"}
```

#### 2) Generate Token (`token.generate`):
```python
# Standard Token (Default expiry: "1H")
res_token = token.generate("auth", {"user_id": 101, "role": "admin"}, expiry="1H")

# Token with Device & IP Binding (Locks token to current device & network)
res_token = token.generate(
    usecase="auth",
    data={"user_id": 101, "role": "admin"},
    expiry="2H",            # Supports: "30M", "1H", "7D", "1MO", "1Y" or seconds
    use_ip=True,            # Token will be valid ONLY from this IP
    use_device=True         # Token will be valid ONLY from this browser/device
)
```

**Success Response (`token.generate`):**
```json
{
  "status": true,
  "token": "v1.wgpNIcq2aaF1yTAjTwXSU6+5pVZM19LndVUW93gqJ5q6wFhTySZzo5mVBlaoZLl0V6m+1mrwGBmSDx4d72r3mrXFzArqVYAPiE0e9LclPZB22rZrCaTCqnlqOV1ZhAKQ2osa3nGDDoIawfFWWaHaJLgdWaM4PtmkUwLlA4l5Lj3WrqR15bkLg4x7V63oVmLtC80Jx16AH2TTnlYIQAVP8o7PgE1n/8wvf4cg/LetXx0hBx5/n4GQTWD+GhK1W+EP6T8nc78/NiXff+4VGZ+/T1nXwFjhYgra8Jwd9MundvkmGN0N/E+enboz6EHTxDzkeTJkUcnqyOKnlGlL+raHX6WHkl3lpb0UE7Fp+hGoFnLBCk906ClqqXT6MiXDm00lmcUZJGCU1sfHN1Vr3G1+WJIXK2XIVdqkcMuCkhg5QQPUhfMKC3P7DW1M1OwLxqsZ88pQ5y/woB9jFxBblgEIdw==",
  "jti": "iXBZR3VsuO6rM_k3IMb5P-2HwyuayFHo29G4KxUeHOA1Y0joDIUiGWZD8lFRcYBXtr7_rAK_iavdr0ls0jXpCg",
  "usecase": "auth",
  "expires_at": 1795547467
}
```

#### 3) Verify Token (`token.verify`):
```python
# Verify token against expected usecase
res_verify = token.verify(auth_token, expected_usecase="auth")
```

**Success Response (`token.verify`):**
```json
{
  "status": true,
  "jti": "iXBZR3VsuO6rM_k3IMb5P-2HwyuayFHo29G4KxUeHOA1Y0joDIUiGWZD8lFRcYBXtr7_rAK_iavdr0ls0jXpCg",
  "usecase": "auth",
  "data": {
    "user_id": 101,
    "role": "admin"
  },
  "meta": {
    "iat": 1795543867,
    "exp": 1795547467,
    "ip_bind": false,
    "device_bind": false,
    "kid": "v1"
  }
}
```

#### 4) Error Responses (`token.verify`):
When a token is missing, expired, or tampered with, `token.verify` returns a clean error dictionary without throwing unhandled exceptions:

* **Token missing or invalid format:**
  ```json
  { "status": false, "error": "invalid_token" }
  ```
* **Token expired:**
  ```json
  { "status": false, "error": "token_expired" }
  ```
* **Client IP changed (`use_ip=True`):**
  ```json
  { "status": false, "error": "ip_mismatch" }
  ```
* **Device or browser changed (`use_device=True`):**
  ```json
  { "status": false, "error": "device_mismatch" }
  ```
* **Tampered payload or fingerprint:**
  ```json
  { "status": false, "error": "fingerprint_mismatch" }
  ```

---

### 8. Argon2id Password Hasher (`password`)
OWASP-recommended standard for secure password hashing with constant-time verification:

```python
# 1) Hash Password
hashed = password.hash("UserSecretPass@123")
# Output: "$argon2id$v=19$m=65536,t=4,p=1$..."

# 2) Verify Password (Returns True or False)
is_valid = password.verify("UserSecretPass@123", hashed)
```

---

### 9. Authenticated AES-256-GCM (`aes`)
Authenticated symmetric encryption with RFC 5869 HKDF key derivation and domain separation:

```python
# 1) Encrypt string, dict, list, or bytes
encrypted_token = aes.e("Secret message", "my_secret_key_123")
json_token = aes.e({"user_id": 101, "role": "admin"}, "my_secret_key_123")
```

**Output Example:**
```text
# encrypted_token:
Nu/K1KrjoXYzrSM0XZsHZS7NTJ41e1gUnwoTMKhfmmhtcFMik0QeRHNn

# json_token:
yRrebhfgTRTEeExeCWoylmKIqZ3NXQF//kZZoBJgsrKhFjliQPtNYDjT/R54M+ai/34hvEvZYD4z9A==
```

```python
# 2) Decrypt back to string (Returns None if wrong key or tampered)
text = aes.d(encrypted_token, "my_secret_key_123")
# Output: "Secret message"

# Decrypt back to dictionary
data = aes.d(json_token, "my_secret_key_123", as_json=True)
# Output: {"user_id": 101, "role": "admin"}
```

---

### 10. Ed25519 Digital Signature Cryptography (`dsc`)
Asymmetric cryptographic key generation, digital signing, and verification:

```python
# 1) Generate Key Pair (private.pem and public.pem)
dscToken("keys/directory")

# 2) Sign Data
signature = dsc({"user_id": 101}, "keys/directory/private.pem")
# Returns: {"data": "...", "token": "..."}

# 3) Verify Signature (Supports entire dict or direct token string)
is_valid = dscVerify({"user_id": 101}, signature, "keys/directory/public.pem")
# or:
is_valid = dscVerify({"user_id": 101}, signature["token"], "keys/directory/public.pem")
```

---

### 11. Base64 Utility (`base`)
Fast Base64 encoding and decoding with native JSON parsing support:

```python
# 1) Encode
token = base.e("Hello World")
json_token = base.e({"user_id": 101, "role": "admin"})

# 2) Decode
text = base.d(token)
data = base.d(json_token, as_json=True)
```

---

## 🗄️ Database Drivers

### 12. MySQL Database Manager (`DB` & `MySQLDB`)
Supports multiple concurrent database targets configured via `.env` JSON strings, connection pooling with SHA-256 configuration hashing, auto-reconnect, colon named parameters (`:param`), and transactional execution:

#### 1) Configuration in `.env`:
```env
user={"DB_HOST":"127.0.0.1","DB_PORT":3306,"DB_NAME":"main_app_db","DB_USER":"root","DB_PASS":"ruyebyr8563476nx7tb3@4#$#$#@21"}
```

#### 2) Database Operations & Queries (`DB.raw`):
```python
# 1. INSERT (Returns affected rowcount)
inserted = DB.raw(
    env("user"),
    "INSERT INTO users (name, email, status) VALUES (:name, :email, :status)",
    {
        "name": "Amit Sharma",
        "email": "amit@example.com",
        "status": "active",
    },
)

# 2. SELECT (Single row)
rows = DB.raw(
    env("user"),
    "SELECT id, name, email, status FROM users WHERE email = :email LIMIT 1",
    {"email": "amit@example.com"},
)
user = rows[0] if rows else None

# 3. SELECT (Multiple rows)
active_users = DB.raw(
    env("user"),
    "SELECT id, name, email FROM users WHERE status = :status ORDER BY id DESC LIMIT 20",
    {"status": "active"},
)

# 4. UPDATE (Record update)
updated = DB.raw(
    env("user"),
    "UPDATE users SET status = :status WHERE email = :email",
    {
        "status": "inactive",
        "email": "amit@example.com",
    },
)

# 5. TRANSACTION (Manual Control with rollback & direct response)
try:
    DB.begin_transaction(env("user"))

    # Step 1: Debit
    debited = DB.raw(
        env("user"),
        "UPDATE wallets SET balance = balance - :amt WHERE user_id = :from_id AND balance >= :amt",
        {"amt": 500, "from_id": 1},
    )
    if debited == 0:
        DB.rollback(env("user"))
        return res.e("Insufficient balance or sender wallet not found", 400)

    # Step 2: Credit
    credited = DB.raw(
        env("user"),
        "UPDATE wallets SET balance = balance + :amt WHERE user_id = :to_id",
        {"amt": 500, "to_id": 2},
    )
    if credited == 0:
        DB.rollback(env("user"))
        return res.e("Receiver wallet not found", 400)

    # Commit after all steps succeed
    DB.commit(env("user"))
    return res.s("Amount transferred successfully")

except Exception as e:
    DB.rollback(env("user"))
    return res.e("Transaction failed: " + str(e), 500)

# 6. DELETE (Record removal)
deleted = DB.raw(
    env("user"),
    "DELETE FROM users WHERE email = :email",
    {"email": "amit@example.com"},
)
```

#### 3) Connection Check (`MySQLDB.is_connected`):
```python
is_ok, err = MySQLDB.is_connected(env("user"))
# Returns: (True, None) or (False, "error message")
```

---

### 13. PostgreSQL Database Manager (`pg`)
Supports multi-database PostgreSQL targets configured via `.env` JSON strings, connection pooling with SHA-256 configuration hashing, automatic liveness checks, colon named parameters (`:param`), and transactional execution:

#### 1) Configuration in `.env`:
```env
pg_user={"DB_HOST":"127.0.0.1","DB_PORT":5432,"DB_NAME":"main_app_db","DB_USER":"postgres","DB_PASS":"your_secure_password"}
```

#### 2) Core Operations with `pg.raw`:
```python
# 1. SELECT (Fetch records as dictionaries)
users = pg.raw(
    env("pg_user"),
    "SELECT id, name, email FROM users WHERE status = :status",
    {"status": "active"},
)

# 2. INSERT (Record creation)
inserted = pg.raw(
    env("pg_user"),
    "INSERT INTO users (name, email) VALUES (:name, :email)",
    {"name": "Satyam", "email": "satyam@example.com"},
)

# 3. INSERT with RETURNING (PostgreSQL Native)
new_user = pg.raw(
    env("pg_user"),
    "INSERT INTO users (name, email) VALUES (:name, :email) RETURNING id, created_at",
    {"name": "Rahul", "email": "rahul@example.com"},
)

# 4. UPDATE (Modify records)
updated = pg.raw(
    env("pg_user"),
    "UPDATE users SET name = :name WHERE email = :email",
    {"name": "Satyam Kumar", "email": "satyam@example.com"},
)

# 5. ATOMIC TRANSACTIONS (Context Manager)
with pg.transaction(env("pg_user")):
    pg.raw(
        env("pg_user"),
        "UPDATE wallets SET balance = balance - :amt WHERE user_id = :id",
        {"amt": 100, "id": 1},
    )
    pg.raw(
        env("pg_user"),
        "UPDATE wallets SET balance = balance + :amt WHERE user_id = :id",
        {"amt": 100, "id": 2},
    )

# 6. DELETE (Record removal)
deleted = pg.raw(
    env("pg_user"),
    "DELETE FROM users WHERE email = :email",
    {"email": "satyam@example.com"},
)

# 7. Connection Check
is_ok, err = pg.is_connected(env("pg_user"))
```

---

### 14. Asynchronous Redis Client (`redis`)
Globally accessible Redis instance with multi-database connection pooling, auto-delegation to default `REDIS_DB=0`, and optional `db` targeting:

```python
# 1) String operations (Default DB: REDIS_DB from .env, defaults to 0)
await redis.set("name", "Satyam")
name = await redis.get("name")

# 2) Specific database via db parameter (e.g. DB 1)
await redis.set("name", "Satyam", db=1)
name = await redis.get("name", db=1)

# 3) Specific database via helper (redis.db(1) or redis(1))
await redis.db(1).set("name", "Satyam")
await redis(1).set("name", "Satyam")

# 4) Delete & Expire
await redis.delete("name")
await redis.expire("name", 300)
# or on specific DB:
await redis.delete("name", db=1)

# 5) Queues / Lists (RPUSH, LRANGE, LPOP)
await redis.rpush("queue", "task1")
tasks = await redis.lrange("queue", 0, -1)
task = await redis.lpop("queue")

# 6) Health Check
is_alive = await redis.isConnected()       # Checks default DB
is_alive_db1 = await redis.isConnected(1)  # Checks DB 1
```

---

### 15. Asynchronous SQLite Driver (`sqlite`)
High-performance asynchronous SQLite connector running in **WAL mode** with query thread-safety:

```python
# Connect to SQLite database file
db = await sqlite.connect("database/app.db")

# Run query
rows = await db.raw("SELECT * FROM users WHERE status = ?", ["active"])
```

---

## 🚀 Running the Server

Start the development server with hot-reload enabled:

```bash
# Using Uvicorn CLI
uvicorn main:app --reload

# Or directly via Python
python main.py
```

---

## 🌐 API Documentation

Once the server is running, explore the interactive documentation:

* **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Structured ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **OpenAPI Specification:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

<div align="center">
  <sub>Built with ❤️ using FastAPI, Cryptography, and Python Asynchronous Architecture.</sub>
</div>
