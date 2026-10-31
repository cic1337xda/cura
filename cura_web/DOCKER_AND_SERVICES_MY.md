# 🐳 Topologi Kontena Docker & Mikroservis

> Spesifikasi orkestrasi kontena, jambatan rangkaian luaran, had saiz log, dan konfigurasi pembolehubah persekitaran.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](DOCKER_AND_SERVICES_MY.md)**
* 🇬🇧 **[English Documentation](DOCKER_AND_SERVICES.md)**

---

## 🌐 Topologi Rangkaian & Komunikasi Antara Servis

Semua servis beroperasi di dalam satu rangkaian bridge luaran yang dikongsi: `pwn20wnd-network`.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     DOCKER BRIDGE: pwn20wnd-network                    │
│                                                                        │
│   ┌────────────────────┐     DNS Dalaman    ┌──────────────────────┐   │
│   │   cura_frontend    │ ─────────────────▶ │    cura_backend      │   │
│   │   Gerbang Nginx    │  http://cura_      │   FastAPI (Python)   │   │
│   │   Port Host: 8087  │  backend:8000/     │   Port Host: 8800    │   │
│   └────────────────────┘                    └──────────┬───────────┘   │
│                                                        │               │
│                                       Kolam asyncpg    │ DNS Dalaman   │
│                                                        ▼               │
│                                             ┌──────────────────────┐   │
│                                             │       cura_db        │   │
│                                             │    PostgreSQL 16     │   │
│                                             │   Port Host: 5440    │   │
│                                             └──────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Matriks Servis Kontena

| Pengenal Servis | Nama Kontena | Imej Asas / Konteks Bina | Port Host Terdedah | Port Dalaman Kontena | Ujian Kesihatan / Dependensi |
|:----------------|:-------------|:-------------------------|:------------------:|:--------------------:|:-----------------------------|
| `cura_db` | `cura_db` | `postgres:16-alpine` | `5440` | `5432` | `pg_isready -U {USER} -d {DB}` |
| `cura_backend` | `cura_backend` | `./backend` (Python 3.12) | `8800` | `8000` | Bergantung pada `cura_db` yang sihat |
| `cura_frontend` | `cura_frontend` | `./frontend` (Nginx + Vue) | `8087` | `80` | Bergantung pada `cura_backend` |

---

## 🔒 Ketahanan Storan Data (Volumes)

1. **`postgres_data`:** Volume Docker yang dipautkan ke `/var/lib/postgresql/data` bagi memastikan rekod pangkalan data tidak hilang semasa kontena dibina semula.
2. **`uploads_data`:** Volume Docker yang dipautkan ke `/app/uploads` dalam `cura_backend` bagi menyimpan gambar profil pesakit dan avatar doktor.

---

## 🛡️ Polisi Had Saiz Log Pengeluaran

Bagi mengelakkan ruang cakera (*disk space*) pelayan penuh tanpa kawalan, had saiz fail log dikuatkuasakan pada ketiga-tiga kontena:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📋 Matriks Pembolehubah Persekitaran (`.env`)

| Nama Pembolehubah | Wajib | Nilai Contoh / Default | Keterangan |
|:------------------|:-----:|:-----------------------|:-----------|
| `TZ` | Ya | `Asia/Kuala_Lumpur` | Zon masa standard hos dan kontena |
| `POSTGRES_DB` | Ya | `cura_hms` | Nama pangkalan data PostgreSQL |
| `POSTGRES_USER` | Ya | `cura_admin` | Nama pengguna pentadbir pangkalan data |
| `POSTGRES_PASSWORD` | Ya | `change_me_pg` | Kata laluan DB (Tukar untuk pengeluaran!) |
| `POSTGRES_PORT` | Ya | `5440` | Port pemetaan luar untuk alatan DB |
| `BACKEND_PORT` | Ya | `8800` | Port pemetaan luar untuk REST API FastAPI |
| `FRONTEND_PORT` | Ya | `8087` | Port pemetaan luar untuk dashboard web Nginx |
| `SECRET_KEY` | Ya | `64_char_random_hex` | Kunci kriptografi untuk menandatangani JWT |

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
