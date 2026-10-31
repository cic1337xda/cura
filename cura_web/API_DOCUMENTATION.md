# 📡 Cura. HMS REST API Specification

> Exhaustive documentation of all REST endpoints, request payloads, response schemas, and error codes.

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](API_DOCUMENTATION.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](API_DOCUMENTATION_MY.md)**

---

## 🔐 1. Authentication Endpoints (`/auth`)

### 1.1 Administrator Login
* **Endpoint:** `POST /auth/admin/login`
* **Request Payload:**
  ```json
  {
    "email": "admin@mail.com",
    "password": "Password@123"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "admin"
  }
  ```

### 1.2 Doctor / Staff Login
* **Endpoint:** `POST /auth/doctor/login`
* **Request Payload:**
  ```json
  {
    "employee_number": "C01A0001",
    "password": "DoctorPassword123"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "doctor"
  }
  ```

---

## 👤 2. Patient Management Endpoints (`/patients`)

### 2.1 Fetch Next Sequential Patient ID
* **Endpoint:** `GET /patients/next-number`
* **Response (200 OK):**
  ```json
  {
    "number": "C00A0003"
  }
  ```

### 2.2 List / Search Patients
* **Endpoint:** `GET /patients?search={query}`
* **Query Parameters:** `search` (Optional: matches `patient_number`, `ic_card_uid`, `ic_number`, `name`, `nationality`)
* **Response (200 OK):** Array of `PatientOut` objects.

### 2.3 Register New Patient
* **Endpoint:** `POST /patients`
* **Request Payload:**
  ```json
  {
    "first_name": "Abdullah",
    "last_name": "Afiq",
    "patient_number": "C00A0001",
    "ic_number": "010203-04-5678",
    "ic_card_uid": "CF289949",
    "nationality": "Malaysian",
    "phone": "+60123456789",
    "date_of_birth": "2001-02-03",
    "age": "25",
    "address": "Kuala Lumpur, Malaysia",
    "patient_type": "OutPatient",
    "ailment": "Hypertension Stage 1"
  }
  ```

### 2.4 Patient Discharge & Re-Admission
* **Discharge:** `PUT /patients/{id}/discharge?status_text=Discharged`
* **Re-admit:** `PUT /patients/{id}/readmit` (Sets `discharge_status = null` while preserving historical records).

### 2.5 Clinical Sub-records for Patient
* `GET /patients/{id}/vitals`
* `GET /patients/{id}/prescriptions`
* `GET /patients/{id}/lab-tests`
* `GET /patients/{id}/surgeries`
* `GET /patients/{id}/medical-records`

---

## 👨‍⚕️ 3. Doctor Management Endpoints (`/doctors`)

* `GET /doctors/next-number` $\rightarrow$ Returns next `C01A####` ID.
* `GET /doctors` $\rightarrow$ List active medical staff.
* `POST /doctors` $\rightarrow$ Register doctor (auto-hashes password via Bcrypt).
* `GET /doctors/{id}` $\rightarrow$ Retrieve doctor profile.
* `PUT /doctors/{id}` $\rightarrow$ Update credentials, department, and MyKad UID.
* `DELETE /doctors/{id}` $\rightarrow$ Remove staff record.

---

## 💊 4. Pharmacy & Operations Endpoints

| Resource | Endpoints | Description |
|:---------|:----------|:------------|
| **Categories** | `GET/POST /pharmacy/categories`, `DELETE /{id}` | Pharmaceutical category grouping |
| **Drugs** | `GET/POST /pharmacy/drugs`, `DELETE /{id}` | Medicine inventory & barcode tracking |
| **Prescriptions** | `GET/POST /pharmacy/prescriptions`, `DELETE /{id}` | Digital prescriptions (`C02A####`) |
| **Laboratory** | `GET/POST /lab/tests`, `DELETE /{id}` | Diagnostic tests & results (`C03A####`) |
| **Vitals** | `GET/POST /lab/vitals`, `DELETE /{id}` | Vital signs records (`C04A####`) |
| **Medical Records** | `GET/POST /records/medical`, `DELETE /{id}` | Medical history notes (`C05A####`) |
| **Surgery** | `GET/POST /records/surgery`, `DELETE /{id}` | Operating theatre schedules (`C06A####`) |
| **Operations** | `GET/POST /ops/{equipment,vendors,accounts,payrolls}` | Hospital assets, suppliers & payrolls |

---

## 🩺 5. System Healthcheck (`/health`)

* **Endpoint:** `GET /health` and `GET /api/v1/health`
* **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-10-31T15:00:00+08:00"
  }
  ```

---

## 📜 License
* Developed for **Educational Purposes Only**.
