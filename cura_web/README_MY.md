# 🏥 Pelantar Web & Backend Cura. HMS

> **Skop:** Mikroservis terkontena, backend tak segerak Python FastAPI, frontend Vue 3 SPA, dan pangkalan data PostgreSQL 16.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](README_MY.md)**
* 🇬🇧 **[English Documentation](README.md)**

---

## 🧭 Seni Bina Subsistem

Pelantar web ini menyelaraskan aliran kerja klinikal merentasi tiga kontena utama yang diorkestrasi melalui Docker Compose:

```text
┌───────────────────────────────┐
│        cura_frontend          │  Vue 3 SPA, Gerbang Nginx, Tema Liquid Glass
│         (Port 8087)           │  Permissions-Policy: "nfc=*" untuk Web NFC API
└───────────────┬───────────────┘
                │ Proksi Reverse /api/ dan /uploads/
                ▼
┌───────────────────────────────┐
│        cura_backend           │  FastAPI (Python 3.12, Uvicorn), Async SQLAlchemy 2.0
│         (Port 8800)           │  Header Sekuriti, X-Request-ID, Penjana ID Deterministik
└───────────────┬───────────────┘
                │ Kolam Sambungan Asyncpg (DNS: cura_db:5432)
                ▼
┌───────────────────────────────┐
│           cura_db             │  Enjin PostgreSQL 16, Kunci Utama UUID
│         (Port 5440)           │  TZ & PGTZ: Asia/Kuala_Lumpur
└───────────────────────────────┘
```

---

## 🛠️ Panduan Topik Terperinci

* 📡 **[Spesifikasi Penuh REST API](API_DOCUMENTATION_MY.md)**: Rujukan lengkap endpoint, struktur payload, dan skema respons JSON.
* 🐳 **[Panduan Docker & Perkhidmatan](DOCKER_AND_SERVICES_MY.md)**: Topologi kontena, matriks pembolehubah persekitaran, dan putaran log.
* 🔒 **[Panduan Seni Bina & Keselamatan](SECURITY_AND_ARCHITECTURE_MY.md)**: Mekanisme kriptografi, token sesi JWT, header keselamatan, dan algoritma ID.

---

## ⚡ Pelancaran & Persediaan

```bash
# Masuk ke direktori web
cd cura_web

# Cipta fail persekitaran
cp .env.example .env

# Jalankan kontena di latar belakang
docker compose up --build -d
```

### Pautan Akses:
* **Dashboard Klinikal:** `http://localhost:8087`
* **Dokumentasi API Interaktif:** `http://localhost:8800/docs`
* **Pemeriksa Kesihatan Sistem:** `http://localhost:8800/health`

### Kredensial Pentadbir Asal:
* **Emel / ID:** `admin@mail.com`
* **Kata Laluan Asal:** `Password@123`

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
