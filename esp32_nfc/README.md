# 📟 ESP32-S3 Dual-Mode NFC Subsystem

> **Scope:** Embedded firmware, hardware transceiver configuration, and browser serial integration for the Cura. HMS clinic terminal.

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](README.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](README_MY.md)**

---

## 🧭 Hardware Overview

The Cura. HMS terminal scanner is an embedded hardware subsystem designed around the **Espressif ESP32-S3** microcontroller and the **NXP/Adafruit PN532** NFC/RFID transceiver.

It performs two simultaneous operational roles over a single native USB connection:
1. **Direct Web Serial Bus:** Streams structured events (`[WEB_READ]:<id>`, `[UI_SUCCESS]`, `[UI_ARMED]`) directly into Google Chrome/Edge via the Web Serial API without requiring operating system drivers.
2. **Native USB HID Keyboard:** Automatically emulates a physical keystroke device, typing scanned identifiers into whatever application input field has active focus.

```text
┌─────────────────┐           I2C Protocol           ┌──────────────────────┐
│  ESP32-S3 MCU   │ ◄──────────────────────────────► │ PN532 NFC Module     │
│  Native USB OTG │ (SDA: GPIO8, SCL: GPIO9, 400kHz) │ 13.56MHz Transceiver │
└────────┬────────┘                                  └──────────┬───────────┘
         │                                                      │
         ▼ USB CDC & HID                                        ▼ RF Field
┌─────────────────┐                                  ┌──────────────────────┐
│ Workstation Web │                                  │ Physical Smart Card  │
│  (Cura. HMS)    │                                  │ (CUID / MyKad / HCE) │
└─────────────────┘                                  └──────────────────────┘
```

---

## 📦 Bill of Materials (BOM)

| Item | Component | Quantity | Description / Specification |
|:----:|:----------|:--------:|:---------------------------|
| 1 | ESP32-S3 DevKitC-1 | 1 | Dual-core Xtensa LX7, 240MHz, Native USB CDC/HID |
| 2 | Adafruit / Elechouse PN532 | 1 | 13.56 MHz RFID/NFC Transceiver with integrated antenna |
| 3 | USB Type-C Cable | 1 | High-speed data cable with differential D+/D- lines |
| 4 | Jumper Wires | 6 | Female-to-Female silicone breadboard jumpers (10 cm) |
| 5 | Target Cards / Stickers | Any | Mifare Classic 1K CUID Gen2/Gen1a (writable Block 0) |

---

## 🛠️ Topic Guides

* 🔌 **[Pinout & Hardware Wiring Guide](PINOUT_AND_WIRING.md)**: Circuit schematics, power rail analysis, and electrical safety.
* ⚡ **[Flashing & Toolchain Setup Guide](FLASHING_AND_SETUP.md)**: Arduino IDE configuration, required board settings, and troubleshooting.

---

## 📜 License
* Developed for **Educational Purposes Only**.
