# Cura. HMS — System Architecture

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](architecture.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](architecture_MY.md)**

---

## Overview

Cura. HMS is a Hospital Management Information System (HMIS) that combines three components:

1. **Web Application (`cura_web`)** — Vue 3 + FastAPI + PostgreSQL hospital management dashboard
2. **Mobile App (`cura_app`)** — Flutter (Android) app that emulates a patient NFC card via Host Card Emulation (HCE)
3. **NFC Scanner (`cura_web/esp32_nfc`)** — ESP32-S3 + PN532 firmware for reading/writing physical Mifare CUID cards

The physical NFC card (or the Android phone acting as a card) carries the patient's 8-character ID. Tapping it on the reader instantly pulls up the patient's record in the dashboard — no typing required.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | **FastAPI** (Python 3.12) | Async, Pydantic validation, SQLAlchemy 2.0 |
| Database | **PostgreSQL 16** | Persistence for all entities |
| Frontend | **Vue 3 + Vite** | SPA; Pinia state; served by Nginx |
| Mobile App | **Flutter (Dart)** | HCE card emulation (cura_app) |
| NFC Hardware | **ESP32-S3 + PN532** | C++ (Arduino) firmware |
| Containerization | **Docker Compose** | 3 services on `pwn20wnd-network` |
| Reverse Proxy / DNS | Nginx Proxy Manager + Cloudflare | Production TLS, no port forwarding |

---

## Runtime Architecture (Docker)

```text
Internet ──▶ Cloudflare (TLS) ──▶ NPM ──▶ (optional)  OR  http://host:FRONTEND_PORT

┌──────────────────────────┐   /api, /uploads    ┌──────────────────────────┐
│ cura_frontend (nginx:80) │ ──────────────────▶ │ cura_backend (uvicorn)  │
│  static Vue SPA          │                     │  :8000                  │
└──────────────────────────┘                     └────────────┬─────────────┘
                                                              │ asyncpg
                                                              ▼
                                                  ┌──────────────────────────┐
                                                  │ cura_db (postgres:16)    │
                                                  │  internal :5432          │
                                                  └──────────────────────────┘
```

### Docker services (`cura_web/docker-compose.yml`)

| Service | Image / Build | Host Port | Purpose |
|---------|---------------|:---:|---------|
| `cura_db` | `postgres:16-alpine` | `${POSTGRES_PORT}` (5440) | Postgres database |
| `cura_backend` | `./backend` | `${BACKEND_PORT}` (8800) | FastAPI REST API |
| `cura_frontend` | `./frontend` | `${FRONTEND_PORT}` (8087) | Nginx serving the Vue SPA + proxying `/api` & `/uploads` |

All containers join the external `pwn20wnd-network` bridge and communicate over Docker DNS.

### Browser ⇄ Hardware integration

```text
                 ┌─────────────────────────────────────────────────┐
   Desktop  ───▶ │ Web Serial API ──▶ ESP32-S3 USB ──▶ PN532      │
                 │    read:  [WEB_READ]:<UID>                     │
                 │    write: WRITE <8-char HEX> ⇄ [UI_SUCCESS] /  │
                 │           [UI_FAILED] / [UI_ARMED]             │
                 ├─────────────────────────────────────────────────┤
   Android  ───▶ │ Web NFC API (NDEFReader) — read-only            │
                 └─────────────────────────────────────────────────┘
```

- **Desktop / laptop:** uses the browser **Web Serial API** to talk directly to the ESP32-S3.
  Can both **scan** (search) and **write** cards.
- **Android phone:** uses the **Web NFC API** (`NDEFReader`). Read-only — the phone
  NFC chip cannot perform the low-level Block 0 rewrite needed to program cards,
  so write features are disabled on mobile.

---

## Data Model & Storage

All entities store a `UUID4` primary key for internal integrity, plus a human-readable,
NFC-compatible **8-character hex ID** for scanning.

### NFC ID format

```
<PREFIX><4-digit zero-padded number>      e.g.  C00A0001
│   │         │
│   │         └── sequential tail (1 – 9999)
│   └──────────── 4-char HEX header (hard-coded per entity)
└──────────────── NFC header "C##A"
```

The backend (`backend/app/core/idgen.py`) is the single source of truth for the next
available number (`GET /patients/next-number`, `GET /doctors/next-number`), avoiding
race conditions from the browser. The form pre-fills the next number, e.g. if
`C00A0002` exists, the new patient form suggests `C00A0003`.

### Entity prefix map

| Entity | Prefix | Example |
|--------|:---:|---------|
| Patient | `C00A` | `C00A0001` |
| Doctor | `C01A` | `C01A0001` |
| Prescription | `C02A` | `C02A0001` |
| Laboratory record | `C03A` | `C03A0001` |
| Vitals record | `C04A` | `C04A0001` |
| Medical record | `C05A` | `C05A0001` |
| Surgery | `C06A` | `C06A0001` |
| Vendor | `C07A` | `C07A0001` |
| Account | `C08A` | `C08A0001` |
| Payroll | `C09A` | `C09A0001` |

### Physical IC Card / MyKad RFID Support
In addition to the normalized CUID tags (`C00A0001`), the system supports scanning and linking physical government identity cards (e.g., Malaysian MyKad with hardware chip UID like `CF289949`).
- Stored under `patients.ic_card_uid` and `doctors.ic_card_uid`.
- Both the search bar and the registration forms allow direct one-tap scanning of physical IC cards.
- Searching by IC UID instantly finds the matching patient or doctor record alongside normal patient IDs.

### Core tables

| Table | Purpose | Notes |
|-------|---------|-------|
| `admins` | Admin accounts | JWT role `admin` |
| `doctors` | Doctor / staff accounts | JWT role `doctor`, hashed password |
| `patients` | Patient core record | `patient_number`, photo, discharge status, type |
| `patient_transfers` | Inter-hospital transfers | linked by `patient_number` |
| `pharmaceuticals` / `pharmaceutical_categories` | Drug inventory | manual barcode |
| `prescriptions` | Prescriptions | linked by `patient_number`; auto `C02A` |
| `laboratory` / `vitals` | Lab tests + vital signs | linked by `patient_number` |
| `medical_records` / `surgeries` | Clinical records | linked by `patient_number` |
| `equipment` / `assets` | Operation equipment | manual code |
| `vendors` | Suppliers | auto `C07A` |
| `accounts` | Payable / Receivable | auto `C08A` |
| `payrolls` | Staff payroll | auto `C09A` |
| `password_resets` | Reset helper | |

> **Relationship rule:** secondary clinical records (vitals, prescriptions, lab,
> surgeries, medical records) reference the patient's **`patient_number` string**
> rather than the UUID. This is what makes the NFC flow possible — the scanned
> 8-char ID maps directly onto those rows, and re-admission keeps the same
> `patient_number` so history stays linked.

---

## Frontend Structure (`cura_web/frontend/src`)

```
├── App.vue                 # Shell: sidebar nav, theme init
├── router/index.js         # Vue Router + auth guard
├── stores/
│   ├── theme.js            # dark/light mode (persisted)
│   └── serial.js           # ESP32 Web Serial manager (Pinia)
├── composables/
│   ├── useDevice.js        # phone vs desktop capability gate
│   └── useDialog.js        # global confirm/alert/image modal
├── components/
│   ├── GlassDialog.vue     # Global modal
│   ├── ScanBar.vue         # Two NFC scan buttons (phone + ESP32)
│   └── NfcWriteButton.vue  # "Write Card" (ESP32 only)
└── views/                  # Dashboard, Patients, Doctors, Pharmacy,
                            # Prescriptions, Laboratory, Vitals, Medical
                            # Records, Surgery, Equipment, Vendors,
                            # Accounts, Payrolls, Settings, Login, Welcome
```

Device-aware gating: the **Phone NFC** scan button is disabled on desktop browsers,
and the **ESP32** scan/write buttons are disabled when opened from a phone.

---

## Backend Structure (`cura_web/backend/app`)

```
├── main.py             # FastAPI app, CORS, lifespan (migrations + seed admin)
├── core/
│   ├── config.py       # settings from .env
│   ├── database.py     # async engine & session
│   ├── security.py     # bcrypt + JWT
│   └── idgen.py        # prefix-based sequential ID generator
├── models/             # SQLAlchemy models (17 tables)
├── schemas/            # Pydantic request/response models
└── routers/            # auth, patients, doctors, pharmacy, laboratory,
                        # records, operations
```

On startup the backend creates tables (if missing), applies idempotent column
migrations (e.g. `photo`, `ic_number`), and seeds the default admin account.

---

## API Summary

| Area | Base path | Endpoints |
|------|-----------|-----------|
| Auth | `/auth` | `admin/login`, `doctor/login` |
| Patients | `/patients` | full CRUD, search, `next-number`, photo, `discharge`, `readmit`, related-record lookups, transfers, dashboard stats |
| Doctors | `/doctors` | CRUD, `next-number`, photo |
| Pharmacy | `/pharmacy` | categories, drugs, prescriptions |
| Lab | `/lab` | tests, vitals |
| Records | `/records` | medical, surgery |
| Ops | `/ops` | equipment, vendors, accounts, payrolls, assets |

---

## Ports

| Service | Internal | External (`.env`) |
|---------|:---:|:---:|
| PostgreSQL | 5432 | 5440 |
| Backend API | 8000 | 8800 |
| Frontend | 80 (nginx) | 8087 |

---

## Security & Data Protection

- **JWT** (HS256, 8h expiry) auth for admin (`email`) and doctor (`employee_number`).
- **bcrypt** password hashing.
- **Secrets live only in `.env`** (`SECRET_KEY`, DB password), which is git-ignored.
- API exposed via CORS; production TLS handled by Cloudflare / Nginx Proxy Manager.
- No sensitive data (passwords, keys) is committed to the repository.

---

## Mobile App (`cura_app`)

Flutter app emulating an NFC card through Android **Host Card Emulation (HCE)**.
- Registered AID: `F222222222`
- SELECT APDU: `00 A4 04 00 05 F2 22 22 22 22 00`
- Responds with `<patient_id> 90 00` (success status word).

See `known_bugs.md` for Android/Samsung HCE quirks and fixes.

---

## 📜 License
* Developed for **Educational Purposes Only**.