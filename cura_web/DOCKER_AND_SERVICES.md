# 🐳 Docker Containers & Microservices Topology

> Specifications for container orchestration, external network bridging, logging limits, and environment variable configuration.

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](DOCKER_AND_SERVICES.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](DOCKER_AND_SERVICES_MY.md)**

---

## 🌐 Network Topology & Inter-Service Discovery

All services reside on an external pre-provisioned bridge network: `pwn20wnd-network`.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        DOCKER BRIDGE: pwn20wnd-network                 │
│                                                                        │
│   ┌────────────────────┐    Internal DNS    ┌──────────────────────┐   │
│   │   cura_frontend    │ ─────────────────▶ │    cura_backend      │   │
│   │   Nginx Gateway    │  http://cura_      │   FastAPI (Python)   │   │
│   │   Host Port: 8087  │  backend:8000/     │   Host Port: 8800    │   │
│   └────────────────────┘                    └──────────┬───────────┘   │
│                                                        │               │
│                                       asyncpg Pool     │ Internal DNS  │
│                                                        ▼               │
│                                             ┌──────────────────────┐   │
│                                             │       cura_db        │   │
│                                             │    PostgreSQL 16     │   │
│                                             │   Host Port: 5440    │   │
│                                             └──────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Container Services Matrix

| Service Identifier | Container Name | Base Image / Build Context | Exposed Host Port | Container Internal Port | Healthcheck / Dependency |
|:-------------------|:---------------|:---------------------------|:-----------------:|:-----------------------:|:-------------------------|
| `cura_db` | `cura_db` | `postgres:16-alpine` | `5440` | `5432` | `pg_isready -U {USER} -d {DB}` |
| `cura_backend` | `cura_backend` | `./backend` (Python 3.12) | `8800` | `8000` | Depends on healthy `cura_db` |
| `cura_frontend` | `cura_frontend` | `./frontend` (Nginx + Vue) | `8087` | `80` | Depends on `cura_backend` |

---

## 🔒 Volume Persistence

1. **`postgres_data`:** Named Docker volume mounted at `/var/lib/postgresql/data` ensuring data persistence across container rebuilds.
2. **`uploads_data`:** Named Docker volume mounted at `/app/uploads` in `cura_backend` storing uploaded patient photos and clinician avatars.

---

## 🛡️ Production Log Rotation Policy

To prevent unbounded disk growth in production, log rotation is enforced across all three containers:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📋 Environment Variable Matrix (`.env`)

| Variable Name | Required | Default / Example Value | Description |
|:--------------|:--------:|:-----------------------|:------------|
| `TZ` | Yes | `Asia/Kuala_Lumpur` | Host and container standard timezone |
| `POSTGRES_DB` | Yes | `cura_hms` | PostgreSQL database name |
| `POSTGRES_USER` | Yes | `cura_admin` | Database administrative username |
| `POSTGRES_PASSWORD` | Yes | `change_me_pg` | Database password (Change in production!) |
| `POSTGRES_PORT` | Yes | `5440` | External mapped port for database tooling |
| `BACKEND_PORT` | Yes | `8800` | External mapped port for FastAPI REST API |
| `FRONTEND_PORT` | Yes | `8087` | External mapped port for Nginx web dashboard |
| `SECRET_KEY` | Yes | `64_char_random_hex` | Cryptographic secret for signing JWT tokens |

---

## 📜 License
* Developed for **Educational Purposes Only**.
