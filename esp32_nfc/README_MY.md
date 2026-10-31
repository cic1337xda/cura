# 📟 Subsistem NFC Dwi-Mod ESP32-S3

> **Skop:** Firmware tertanam, konfigurasi transceiver perkakasan, dan integrasi serial pelayar web untuk stesen kaunter Cura. HMS.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](README_MY.md)**
* 🇬🇧 **[English Documentation](README.md)**

---

## 🧭 Gambaran Keseluruhan Perkakasan

Pengimbas terminal Cura. HMS merupakan subsistem perkakasan tertanam yang dibina berasaskan mikropengawal **Espressif ESP32-S3** dan transceiver NFC/RFID **NXP/Adafruit PN532**.

Perkakasan ini melaksanakan dua peranan serentak melalui satu sambungan kabel USB:
1. **Bas Web Serial Terus:** Menghantar data berstruktur (`[WEB_READ]:<id>`, `[UI_SUCCESS]`, `[UI_ARMED]`) terus ke pelayar web Google Chrome/Edge melalui Web Serial API tanpa memerlukan pemasangan driver OS tambahan.
2. **Papan Kekunci USB HID Asli:** Meniru papan kekunci fizikal secara automatik, menaip nombor UID pesakit ke dalam mana-mana kotak input yang sedang aktif.

```text
┌─────────────────┐           Protokol I2C           ┌──────────────────────┐
│  MCU ESP32-S3   │ ◄──────────────────────────────► │ Modul NFC PN532      │
│  Native USB OTG │ (SDA: GPIO8, SCL: GPIO9, 400kHz) │ Transceiver 13.56MHz │
└────────┬────────┘                                  └──────────┬───────────┘
         │                                                      │
         ▼ USB CDC & HID                                        ▼ Medan RF
┌─────────────────┐                                  ┌──────────────────────┐
│ Komputer Kaunter│                                  │ Kad Pintar Fizikal   │
│  (Cura. HMS)    │                                  │ (CUID / MyKad / HCE) │
└─────────────────┘                                  └──────────────────────┘
```

---

## 📦 Senarai Bahan Perkakasan (BOM)

| Bil | Komponen | Kuantiti | Keterangan / Spesifikasi |
|:---:|:---------|:--------:|:-------------------------|
| 1 | ESP32-S3 DevKitC-1 | 1 | Dwi-teras Xtensa LX7, 240MHz, USB CDC/HID Asli |
| 2 | Adafruit / Elechouse PN532 | 1 | Transceiver RFID/NFC 13.56 MHz dengan antena terbina |
| 3 | Kabel USB Type-C | 1 | Kabel data berkelajuan tinggi dengan talian pembeza D+/D- |
| 4 | Wayar Pelompat (Jumper) | 6 | Female-to-Female silikon (10 cm) |
| 5 | Kad / Pelekat Sasaran | Mana-mana | Mifare Classic 1K CUID Gen2/Gen1a (Blok 0 boleh tulis) |

---

## 🛠️ Panduan Terperinci

* 🔌 **[Panduan Sambungan Pin & Pendawaian](PINOUT_AND_WIRING_MY.md)**: Skematik litar, analisis rel kuasa, dan keselamatan elektrik.
* ⚡ **[Panduan Flashing & Persediaan Toolchain](FLASHING_AND_SETUP_MY.md)**: Tetapan Arduino IDE, pilihan board, dan penyelesaian masalah.

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
