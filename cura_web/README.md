# Cura. HMS (Hospital Management System)

Cura. HMS is a modern, full-stack Hospital Management Information System designed to streamline hospital operations, manage patient flow, and interface seamlessly with physical NFC smart cards for rapid patient and doctor identification.

## Table of Contents
1. [Overview & Scope](#overview--scope)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Data Storage & ID Generation](#data-storage--id-generation)
5. [NFC Integration](#nfc-integration)
6. [Getting Started (Docker)](#getting-started-docker)
7. [Environment Variables](#environment-variables)
8. [License](#license)

---

## Overview & Scope
Cura. is built to digitize core medical workflows. The primary scope of the project encompasses:
- **Patient Management:** Admissions, discharges, vital signs, lab tests, surgeries, and comprehensive medical histories.
- **Staff Management:** Doctor accounts, directory, and payroll processing.
- **Pharmacy & Inventory:** Pharmaceutical stock tracking, drug categorizations, and digital prescriptions.
- **Operations:** Equipment/Asset tracking, vendor relations, and payable/receivable accounts.
- **Physical Integration:** Linking physical NFC smart cards (or Android NFC devices) directly to digital records via browser-based APIs.

---

## Key Features
- **Glassmorphism UI:** A highly polished, responsive Vue 3 frontend utilizing a modern iOS-inspired "liquid glass" aesthetic with seamless Light/Dark mode transitions.
- **Device-Aware NFC Scanning:**
  - **Phone NFC:** Leverages the experimental Web NFC API (`NDEFReader`) allowing Android phones to scan cards directly via the browser.
  - **Desktop NFC:** Leverages the Web Serial API to communicate directly with an ESP32-S3 custom hardware scanner, completely bypassing OS-level middleware.
- **Card Programming:** Program patient IDs onto physical CUID cards directly from the browser's "Patient Detail" page via the ESP32-S3 hardware.
- **Auto-Incrementing Entity IDs:** Unique, alphanumeric identifiers generated synchronously by the backend (e.g., Patient `C00A0001`, Doctor `C01A0001`).
- **Scan on every list page:** A two-button scanner bar (Phone NFC / ESP32) is available across all modules — scan, and the list filters instantly.
- **Settings page:** Choose Light/Dark theme and manage the ESP32 serial connection (saved ports + add device).
- **Doctor management:** Full add/edit/view/delete with auto-incrementing employee IDs.
- **Discharge & Re-admit:** Discharge a patient or re-admit them later — the patient number and full history are preserved.

---

## Architecture
The system employs a containerized microservices architecture.

```text
┌─────────────────────┐       HTTP / REST (Axios)       ┌────────────────────────┐
│   Vue 3 Frontend    │ ──────────────────────────────▶ │  FastAPI Backend (Py)  │
│  (Nginx, Port 80)   │                                 │ (Uvicorn, Port 8000)   │
└─────────────────────┘                                 └────────────────────────┘
           │                                                         │
           │ Web Serial API                                          │ asyncpg
           ▼                                                         ▼
┌─────────────────────┐                                 ┌────────────────────────┐
│ ESP32-S3 USB Reader │                                 │  PostgreSQL 16 DB      │
│  (PN532 NFC Module) │                                 │  (Port 5432)           │
└─────────────────────┘                                 └────────────────────────┘
```

1. **Frontend:** Vue.js 3 single-page application bundled with Vite. State management via Pinia. Deployed via an Nginx reverse proxy which also handles API routing and enforces strict `Permissions-Policy` headers required for Web NFC.
2. **Backend:** FastAPI (Python 3.12) utilizing asynchronous endpoints. Handles business logic, JWT authentication, and sequential ID generation.
3. **Database:** PostgreSQL 16 managed asynchronously via SQLAlchemy 2.0.
4. **Hardware Endpoint:** An ESP32-S3 microcontroller running custom C++ firmware, connected via USB.

---

## Data Storage & ID Generation
Data is persisted in a relational PostgreSQL database utilizing `UUID4` primary keys for robust internal references.

To provide human-readable, easily scannable IDs (crucial for NFC limits), the system utilizes a **Prefix + Sequential Auto-Increment** strategy. When an entity is created, the backend scans existing records and assigns the next available sequential number appended to a 4-character HEX prefix.

### Entity Prefix Map
| Entity | Prefix | Example Output |
|--------|--------|----------------|
| **Patient** | `C00A` | `C00A0001` |
| **Doctor** | `C01A` | `C01A0001` |
| **Prescription** | `C02A` | `C02A0001` |
| **Laboratory** | `C03A` | `C03A0001` |
| **Vitals** | `C04A` | `C04A0001` |
| **Medical Record** | `C05A` | `C05A0001` |
| **Surgery** | `C06A` | `C06A0001` |
| **Vendor** | `C07A` | `C07A0001` |
| **Account** | `C08A` | `C08A0001` |
| **Payroll** | `C09A` | `C09A0001` |

*Note: The IDs are strictly formatted to 8-character HEX strings to fit perfectly into the 4-byte UID space of Mifare Classic Block 0.*

---

## NFC Integration

Cura features a highly advanced, browser-native hardware integration. 
There are two scanning modalities:

1. **Mobile (Android Chrome):** Uses the `NDEFReader` Web API. Due to hardware limitations, phones can **read** tags but cannot perform the low-level Block 0 formatting required to *write* the specialized patient IDs to blank cards.
2. **Desktop (Windows/Mac/Linux Chrome):** Uses the Web Serial API (`navigator.serial`). The browser opens a direct serial pipe to the ESP32-S3 via USB.
   - **Reading:** Listens for `[WEB_READ]:<uid>` events emitted by the hardware.
   - **Writing:** The browser sends `WRITE C00A0001\n` to the hardware. The hardware attempts a Block 0 overwrite on the physical card, communicating status (`[UI_ARMED]`, `[UI_SUCCESS]`, `[UI_FAILED]`) back to the Vue UI to trigger popups.

*See the `esp32_nfc/` folder for the hardware schematic and C++ firmware code.*

---

## Getting Started (Docker)

The entire software stack is Dockerized for zero-configuration deployment.

### Prerequisites
- Docker & Docker Compose
- (Optional) Google Chrome / Edge for NFC/Serial API support.

### Running the System
1. Clone the repository.
2. Copy the environment configuration:
   ```bash
   cp .env.example .env
   ```
3. Boot the stack:
   ```bash
   docker compose up --build -d
   ```
4. Access the application:
   - **Frontend:** `http://localhost:8087` (or the port defined in `.env`)
   - **Backend API Docs:** `http://localhost:8800/docs`

Upon first boot, the system automatically runs database migrations and seeds a default administrator account:
- **Email:** `admin@mail.com`
- **Password:** `Password@123`

---

## Environment Variables
Ensure your `.env` file is properly configured before deployment. **Never commit the `.env` file to version control.**

- `TZ`: System timezone (e.g., `Asia/Kuala_Lumpur`).
- `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD`: Database credentials.
- `POSTGRES_PORT` / `BACKEND_PORT` / `FRONTEND_PORT`: Exposed host ports.
- `SECRET_KEY`: A cryptographically secure 64-character string used for signing JWT authentication tokens. **Do not use the placeholder in production.**

---

## License
**Proprietary & Confidential**  
All rights reserved. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited without explicit permission.

---

## Related docs
- Repo overview & setup: [`../README.md`](../README.md)
- Deep architecture & data model: [`../architecture.md`](../architecture.md)
- Hardware firmware: [`esp32_nfc/README.md`](esp32_nfc/README.md)
- Bugs & fixes: [`../known_bugs.md`](../known_bugs.md)