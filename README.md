# Cura. HMS — Hospital Management System

A full-stack **Hospital Management Information System (HMIS)** with real **NFC
card integration**: the dashboard can scan physical RFID cards or Android phones
(card emulation) to instantly identify patients and doctors.

> **One system, three components:**
> `cura_web` (web dashboard + API + ESP32 firmware) · `cura_app` (Android NFC card emulation) · docs

---

## Table of Contents

1. [What it does](#what-it-does)
2. [Repo structure](#repo-structure)
3. [How everything fits together](#how-everything-fits-together)
4. [NFC flow](#nfc-flow)
5. [Running the web system](#running-the-web-system)
6. [Running the Android app](#running-the-android-app)
7. [Firmware & hardware](#firmware--hardware)
8. [Default accounts](#default-accounts)
9. [Configuration & security](#configuration--security)
10. [Documentation](#documentation)
11. [License](#license)

---

## What it does

- **Patient management** — register, search, view, edit, discharge and **re-admit** patients.
- **Clinical workflows** — vital signs, lab tests, prescriptions, medical records, surgeries.
- **Staff & pharmacy** — doctor accounts, drug inventory & categories, digital prescriptions.
- **Operations** — equipment/assets, vendors, accounts, payroll.
- **NFC identification** — tap a physical card **or** an Android phone at the reader to pull up
  the patient within seconds (no typing needed).
- **Card programming** — write the patient ID onto a physical Mifare **CUID** card straight
  from the web dashboard using the ESP32-S3.
- **Auto-increment IDs** — every entity gets a stable, human-readable `C00A0001`-style ID
  that fits the NFC card's 4-byte UID space.
- **Device-aware scanning** — the browser shows the correct scanner for the device you're on
  (phone NFC on phones, ESP32 via USB on desktops).

---

## Repo structure

```
Amjad/
├── README.md               # This document (start here)
├── architecture.md         # Deep-dive: architecture, data model, API, ports
├── known_bugs.md           # Hardware / Android bugs & fixes log
├── LICENSE                 # Proprietary — all rights reserved
│
├── cura_web/               # WEB SYSTEM
│   ├── README.md           # Web dashboard docs
│   ├── docker-compose.yml  # db + backend + frontend
│   ├── backend/            # FastAPI (Python) — REST API, models, idgen
│   ├── frontend/           # Vue 3 + Vite SPA — dashboard UI, NFC & serial
│   └── esp32_nfc/          # ESP32-S3 firmware + its README
│
├── cura_app/               # ANDROID APP (HCE card emulation)
│   ├── README.md
│   ├── lib/                # Flutter UI + card store
│   └── android/            # HCE service, AID registration
│
└── (excluded from git)     # Reference/, Backups/, "Esp32 & Testing codes/", *.env
```

---

## How everything fits together

```text
 ┌─────────────────────────────────────────────────────────────────────┐
 │                         cura_web (Docker)                          │
 │                                                                     │
 │  cura_frontend (Nginx, Vue SPA) ──/api,/uploads──▶ cura_backend     │
 │                                                         │  asyncpg  │
 │                                                         ▼           │
 │                                                  cura_db (Postgres) │
 └─────────────────────────────────────────────────────────────────────┘
        ▲                                              ▲
        │ Web Serial API (USB)                        │ Web NFC / NDEFReader
        │                                              │
   ESP32-S3 + PN532                               Android phone
   (read + write CUID)                            (cura_app — HCE card)
```

- **Desktop/laptop browsers** talk to the **ESP32-S3** over USB with the Web Serial API —
  full read **and** write.
- **Android phones** can **read** NFC tags directly in the browser (Web NFC), and the
  `cura_app` lets the phone *behave as* the patient's card via HCE when held to the reader.
- The **patient/doctor ID** on the card is the same `C00A0001`-format ID stored in the
  database, so a tap == a lookup.

---

## NFC flow

### Scan (search)
```text
tap card/phone
   → reader captures 8-char ID
   → browser search box is filled & patients list filters
   → click the row to open the full record
```

### Write (program a blank card)
```text
Patient Detail → "Write Card"
   → browser sends:  WRITE C00A0001<CR>
   → ESP32 arms [UI_ARMED] → "tap card now"
   → on success [UI_SUCCESS] / on failure [UI_FAILED] popups
```
Writing requires **CUID (Gen2/Gen1a)** Mifare cards — standard cards lock Block 0.

---

## Running the web system

Prerequisites: Docker + Docker Compose, Google Chrome/Edge.

```bash
cd cura_web
cp .env.example .env      # then edit credentials if desired
docker compose up --build -d
```

| What | URL |
|------|-----|
| Dashboard | `http://localhost:8087` |
| API docs (Swagger) | `http://localhost:8800/docs` |

> Ports come from `.env` (`FRONTEND_PORT`, `BACKEND_PORT`, `POSTGRES_PORT`).

---

## Running the Android app

```bash
cd cura_app
flutter pub get
flutter run          # Android device with NFC
```

See [`cura_app/README.md`](cura_app/README.md). On Samsung phones you must set
the app as the default Tap & Pay service for HCE to work.

---

## Firmware & hardware

`cura_web/esp32_nfc/esp32_s3_scanner.ino` targets the **ESP32-S3 + Adafruit PN532**
(I2C: SDA=8, SCL=9; HID + Web Serial).

- Must have **USB CDC On Boot = Enabled** in Arduino IDE.
- Protocol lines the dashboard listens for: `[WEB_READ]:<uid>`, `[UI_ARMED]`,
  `[UI_SUCCESS]`, `[UI_FAILED]`.
- See [`cura_web/esp32_nfc/README.md`](cura_web/esp32_nfc/README.md).

---

## Default accounts

On first startup the backend seeds one administrator.

| Role | Login | Password |
|------|-------|----------|
| Admin | `admin@mail.com` | `Password@123` |

Doctors log in with their **employee number** (e.g. `C01A0001`) + the password set for them.

---

## Configuration & security

- **Never commit `.env`.** The repo ships only `.env.example` with placeholders.
- Set a strong `SECRET_KEY` in production (JWT signing).
- Change the seeded admin password after first login.
- Git-ignored: `Reference/`, `Backups/`, `Esp32 & Testing codes/`, `ocsession.txt`,
  databases, uploads, build artifacts.

---

## Documentation

| Doc | Contents |
|-----|----------|
| [`architecture.md`](architecture.md) | Architecture diagram, tech stack, data model, ID scheme, API, ports |
| [`cura_web/README.md`](cura_web/README.md) | Web dashboard-specific docs |
| [`esp32_nfc/README.md`](cura_web/esp32_nfc/README.md) | Hardware wiring, deps, upload steps |
| [`cura_app/README.md`](cura_app/README.md) | Android HCE app docs |
| [`known_bugs.md`](known_bugs.md) | Known bugs & workarounds (PN532, Android 16, Samsung) |

---

## License

**Proprietary & Confidential** — all rights reserved. This is a closed source
Final Year Project; do not copy, modify, or redistribute without permission.