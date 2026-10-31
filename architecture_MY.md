# Cura. HMS — Seni Bina Sistem

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](architecture_MY.md)**
* 🇬🇧 **[English Documentation](architecture.md)**

---

## Gambaran Keseluruhan

Cura. HMS merupakan Sistem Pengurusan Maklumat Hospital (HMIS) yang menggabungkan tiga komponen utama:

1. **Aplikasi Web (`cura_web`)** — Dashboard pengurusan hospital berasaskan Vue 3 + FastAPI + PostgreSQL.
2. **Aplikasi Mudah Alih (`cura_app`)** — Aplikasi Flutter (Android) untuk pesakit membawa kad perubatan digital melalui Host Card Emulation (HCE).
3. **Pengimbas NFC (`esp32_nfc`)** — Firmware mikropengawal ESP32-S3 + transceiver PN532 untuk membaca dan memprogram kad fizikal Mifare CUID.

Kad fizikal (atau telefon pintar yang bertindak sebagai kad) membawa nombor identiti pesakit berformat 8-aksara. Merapatkan kad ke pengimbas akan membuka rekod pesakit serta-merta tanpa sebarang input menaip secara manual.

---

## Lapisan Teknologi

| Lapisan | Teknologi | Catatan |
|:--------|:----------|:--------|
| Backend | **FastAPI** (Python 3.12) | Asynchronous, validasi Pydantic, SQLAlchemy 2.0 ORM |
| Pangkalan Data | **PostgreSQL 16** | Storan data hubungan dengan kunci primer UUID |
| Frontend | **Vue 3 + Vite** | SPA, pengurusan keadaan Pinia, dihoskan oleh Nginx |
| Aplikasi Mudah Alih | **Flutter (Dart)** | Emulasi kad HCE peranti Android |
| Perkakasan Pengimbas | **ESP32-S3 + PN532** | Firmware C++ Arduino dengan USB CDC/HID |
| Kontena | **Docker Compose** | 3 perkhidmatan pada rangkaian `pwn20wnd-network` |

---

## Seni Bina Runtime (Docker)

```text
Pengguna Web ──▶ Gerbang Nginx (Port 8087) ──▶ FastAPI Backend (Port 8800)
                        │                                │ asyncpg
                        │ Proksi /api/ & /uploads/       ▼
                        └──────────────────────▶ PostgreSQL 16 (Port 5440)
```

---

## Format & Penjanaan ID Deterministik

Setiap entiti menggunakan format awalan heksadesimal 4-aksara yang diikuti dengan 4-digit angka bersiri:

```text
[ AWALAN ]  [ AKHIRAN ANGKA ]
  C00A            0001         =  C00A0001 (Rentetan HEX 8-aksara)
```

| Entiti | Awalan | Contoh Output |
|:-------|:------:|:--------------|
| Pesakit | `C00A` | `C00A0001` |
| Doktor / Staf | `C01A` | `C01A0001` |
| Preskripsi | `C02A` | `C02A0001` |
| Ujian Makmal | `C03A` | `C03A0001` |
| Tanda Vital | `C04A` | `C04A0001` |
| Rekod Perubatan | `C05A` | `C05A0001` |
| Pembedahan | `C06A` | `C06A0001` |
| Pembekal | `C07A` | `C07A0001` |
| Akaun | `C08A` | `C08A0001` |
| Penggajian | `C09A` | `C09A0001` |

### Sokongan Cip MyKad Malaysia
Selain tag CUID format `C00A####`, sistem menyokong pembacaan UID cip perkakasan MyKad (contoh: `CF289949`). Data cip disimpan pada medan `ic_card_uid` dalam rekod pesakit dan doktor bagi membolehkan imbasan satu sentuhan di kaunter.

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
