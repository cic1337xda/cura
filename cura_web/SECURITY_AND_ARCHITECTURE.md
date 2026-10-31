# 🔒 Security, Cryptography & Architecture Specification

> In-depth technical breakdown of cryptographic implementations, authentication lifetimes, deterministic ID algorithms, and security middleware.

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](SECURITY_AND_ARCHITECTURE.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](SECURITY_AND_ARCHITECTURE_MY.md)**

---

## 🛡️ 1. Authentication & Session Lifetimes

1. **Password Hashing:**
   - Passwords for administrators and doctors are hashed using **Bcrypt** with salt generation performed automatically via `passlib.context.CryptContext`.
   - Raw plaintext passwords are never logged, serialized, or stored in database tables.
2. **Stateless JWT Tokens:**
   - Sessions utilize JSON Web Tokens (JWT) signed via **HMAC-SHA256 (`HS256`)**.
   - Token claims contain:
     - `sub`: User unique identifier
     - `role`: Authorization scope (`admin` or `doctor`)
     - `doc_number`: Doctor employee ID (when role is doctor)
     - `exp`: Timestamp expiration (Default: 480 minutes / 8 hours)

---

## 🚦 2. Security Middleware & Request Tracing

Registered in `app/core/middleware.py`, the `SecurityAndTracingMiddleware` intercepts all incoming requests:

1. **Request Tracing (`X-Request-ID`):**
   - Automatically generates a unique `UUID4` for each request (or preserves incoming client correlation IDs).
   - Injected into the HTTP response header `X-Request-ID` to facilitate rapid debugging in reverse proxy logs.
2. **Clickjacking Defense:**
   - Injects `X-Frame-Options: DENY`, preventing the dashboard from being embedded inside malicious `<frame>`, `<iframe>`, or `<embed>` tags.
3. **MIME Sniffing Prevention:**
   - Injects `X-Content-Type-Options: nosniff` to compel browsers to adhere to declared Content-Type headers.
4. **Referrer Policy:**
   - Injects `Referrer-Policy: strict-origin-when-cross-origin` to prevent leaking private path tokens to external domains.

---

## 🔢 3. Deterministic Sequential ID Generation

All entities avoid exposed integer autoincrement sequences. Instead, the centralized generator (`app/core/idgen.py`) allocates a structured **4-character HEX prefix + 4-digit zero-padded integer** (`C##A####`).

```text
[ PREFIX ] [ NUMERIC SUFFIX ]
   C00A           0001        =  C00A0001 (8-character HEX string)
```

### Entity Prefix Matrix:
* `C00A`: Patients
* `C01A`: Doctors / Practitioners
* `C02A`: Prescriptions
* `C03A`: Laboratory Tests
* `C04A`: Vital Signs Records
* `C05A`: Comprehensive Medical Records
* `C06A`: Surgical Schedules
* `C07A`: Suppliers & Vendors
* `C08A`: Accounts (Payable/Receivable)
* `C09A`: Staff Payrolls

### Why 8-Character HEX?
Mifare Classic NFC smart cards contain a manufacturer Block 0 UID consisting of **exactly 4 bytes (32 bits)**, represented in hexadecimal as 8 characters (`0x00` - `0xFF` x 4). By formatting IDs into `C00A0001`, the clinical database identifier maps directly into the physical hardware chip space without requiring secondary translation lookup tables.

---

## 🪪 4. Dual-Mode Smart Card & MyKad Security

1. **Malaysian MyKad Support (`ic_card_uid`):**
   - Physical MyKad cards contain an encrypted contactless chip. The terminal reads the unencrypted hardware UID (e.g. `CF289949`).
   - The chip UID is indexed as an identity pointer, but sensitive biometric and NRIC details are kept exclusively within the protected hospital database.
2. **CUID Block 0 Magic Card Safety:**
   - Standard Mifare cards have Block 0 permanently locked at the factory. Writing to Block 0 requires specialized CUID Gen2 or Gen1a cards.
   - The firmware executes a dual authentication sequence (`defaultKeyA: 0xFF...FF`) and verifies the written block before signalling `[UI_SUCCESS]` to the web dashboard.

---

## 📜 License
* Developed for **Educational Purposes Only**.
