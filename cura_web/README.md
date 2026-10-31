# 🏥 Cura. HMS Web Stack & Backend Platform

> **Scope:** Containerized microservices, asynchronous Python FastAPI backend, Vue 3 SPA frontend, and PostgreSQL 16 database.

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](README.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](README_MY.md)**

---

## 🧭 Subsystem Architecture

The web platform coordinates the clinical workflow across three core containers orchestrated via Docker Compose:

```text
┌───────────────────────────────┐
│        cura_frontend          │  Vue 3 SPA, Nginx Gateway, Liquid Glass Theme
│         (Port 8087)           │  Permissions-Policy: "nfc=*" for Web NFC API
└───────────────┬───────────────┘
                │ /api/ and /uploads/ Reverse Proxy
                ▼
┌───────────────────────────────┐
│        cura_backend           │  FastAPI (Python 3.12, Uvicorn), Async SQLAlchemy 2.0
│         (Port 8800)           │  Security Headers, X-Request-ID, Deterministic ID Gen
└───────────────┬───────────────┘
                │ Asyncpg Connection Pool (DNS: cura_db:5432)
                ▼
┌───────────────────────────────┐
│           cura_db             │  PostgreSQL 16 Engine, UUID Primary Keys
│         (Port 5440)           │  TZ & PGTZ: Asia/Kuala_Lumpur
└───────────────────────────────┘
```

---

## 🛠️ Topic Documentation Guides

* 📡 **[REST API Specifications](API_DOCUMENTATION.md)**: Complete endpoint reference, payload structures, and response schemas.
* 🐳 **[Docker & Services Guide](DOCKER_AND_SERVICES.md)**: Container topology, environment variables, port mappings, and log rotation.
* 🔒 **[Security & Architecture Guide](SECURITY_AND_ARCHITECTURE.md)**: Cryptographic mechanisms, JWT sessions, security headers, and ID algorithms.

---

## ⚡ Deployment & Startup

```bash
# Enter directory
cd cura_web

# Copy environment configuration
cp .env.example .env

# Start stack in detached mode
docker compose up --build -d
```

### Access URLs:
* **Clinical Dashboard:** `http://localhost:8087`
* **API Documentation:** `http://localhost:8800/docs`
* **Healthcheck Probe:** `http://localhost:8800/health`

### Initial Administrator Credentials:
* **Username / Email:** `admin@mail.com`
* **Default Password:** `Password@123`

---

## 📜 License
* Developed for **Educational Purposes Only**.
