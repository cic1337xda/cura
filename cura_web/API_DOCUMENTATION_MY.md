# 📡 Spesifikasi Penuh REST API Cura. HMS

> Dokumentasi terperinci untuk semua endpoint REST, struktur payload penghantaran, skema respons, dan kod ralat.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](API_DOCUMENTATION_MY.md)**
* 🇬🇧 **[English Documentation](API_DOCUMENTATION.md)**

---

## 🔐 1. Endpoint Pengesahan Pengguna (`/auth`)

### 1.1 Log Masuk Pentadbir (Admin)
* **Endpoint:** `POST /auth/admin/login`
* **Payload Permintaan:**
  ```json
  {
    "email": "admin@mail.com",
    "password": "Password@123"
  }
  ```
* **Respons Berjaya (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "admin"
  }
  ```

### 1.2 Log Masuk Doktor / Staf
* **Endpoint:** `POST /auth/doctor/login`
* **Payload Permintaan:**
  ```json
  {
    "employee_number": "C01A0001",
    "password": "DoctorPassword123"
  }
  ```
* **Respons Berjaya (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "doctor"
  }
  ```

---

## 👤 2. Pengurusan Rekod Pesakit (`/patients`)

### 2.1 Dapatkan Nombor ID Pesakit Seterusnya
* **Endpoint:** `GET /patients/next-number`
* **Respons (200 OK):**
  ```json
  {
    "number": "C00A0003"
  }
  ```

### 2.2 Senarai & Carian Pesakit
* **Endpoint:** `GET /patients?search={kata_kunci}`
* **Parameter:** `search` (Pilihan: memadankan `patient_number`, `ic_card_uid`, `ic_number`, nama, dan kewarganegaraan)
* **Respons (200 OK):** Senarai array objek `PatientOut`.

### 2.3 Pendaftaran Pesakit Baharu
* **Endpoint:** `POST /patients`
* **Payload Permintaan:**
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

### 2.4 Pelepasan Wad (Discharge) & Kemasukan Semula (Re-Admit)
* **Discharge:** `PUT /patients/{id}/discharge?status_text=Discharged`
* **Kemasukan Semula:** `PUT /patients/{id}/readmit` (Menetapkan `discharge_status = null` sambil mengekalkan sejarah rawatan asal).

### 2.5 Sub-Rekod Klinikal Pesakit
* `GET /patients/{id}/vitals`
* `GET /patients/{id}/prescriptions`
* `GET /patients/{id}/lab-tests`
* `GET /patients/{id}/surgeries`
* `GET /patients/{id}/medical-records`

---

## 👨‍⚕️ 3. Pengurusan Doktor (`/doctors`)

* `GET /doctors/next-number` $\rightarrow$ Pulangkan ID pekerja `C01A####` seterusnya.
* `GET /doctors` $\rightarrow$ Senarai doktor berdaftar.
* `POST /doctors` $\rightarrow$ Daftar akaun doktor baharu (kata laluan di-hash automatik dengan Bcrypt).
* `GET /doctors/{id}` $\rightarrow$ Profil doktor.
* `PUT /doctors/{id}` $\rightarrow$ Kemaskini jabatan, emel, kata laluan, dan MyKad UID.
* `DELETE /doctors/{id}` $\rightarrow$ Padam akaun doktor.

---

## 💊 4. Modul Farmasi & Operasi

| Sumber | Endpoint | Keterangan |
|:-------|:---------|:-----------|
| **Kategori Ubat** | `GET/POST /pharmacy/categories`, `DELETE /{id}` | Pengelompokan kategori farmaseutikal |
| **Ubat-Ubatan** | `GET/POST /pharmacy/drugs`, `DELETE /{id}` | Inventori ubat & imbasan kod bar |
| **Preskripsi** | `GET/POST /pharmacy/prescriptions`, `DELETE /{id}` | Preskripsi rawatan digital (`C02A####`) |
| **Makmal** | `GET/POST /lab/tests`, `DELETE /{id}` | Ujian & keputusan makmal (`C03A####`) |
| **Tanda Vital** | `GET/POST /lab/vitals`, `DELETE /{id}` | Bacaan tekanan darah, suhu, dll (`C04A####`) |
| **Rekod Perubatan**| `GET/POST /records/medical`, `DELETE /{id}` | Nota sejarah klinikal pesakit (`C05A####`) |
| **Pembedahan** | `GET/POST /records/surgery`, `DELETE /{id}` | Jadual dewan bedah (`C06A####`) |
| **Operasi** | `GET/POST /ops/{equipment,vendors,accounts,payrolls}` | Aset alatan, pembekal & penggajian staf |

---

## 🩺 5. Pemeriksaan Kesihatan Pelayan (`/health`)

* **Endpoint:** `GET /health` dan `GET /api/v1/health`
* **Respons (200 OK):**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-10-31T15:00:00+08:00"
  }
  ```

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
