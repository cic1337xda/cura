# ⚡ Panduan Persediaan Toolchain & Flashing Firmware

> Langkah demi langkah untuk mengkompilasi dan memuat naik (flash) firmware pengimbas dwi-mod CUID & HCE ke mikropengawal ESP32-S3.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](FLASHING_AND_SETUP_MY.md)**
* 🇬🇧 **[English Documentation](FLASHING_AND_SETUP.md)**

---

## 🛠️ Keperluan Asas & Persediaan Arduino IDE

1. **Pasang Arduino IDE:** Muat turun versi 2.x terkini daripada [arduino.cc](https://www.arduino.cc/en/software).
2. **Tambah Pakej Board ESP32:**
   - Buka **File $\rightarrow$ Preferences $\rightarrow$ Additional Board Manager URLs**.
   - Masukkan: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - Buka **Tools $\rightarrow$ Board $\rightarrow$ Boards Manager**, cari `esp32` oleh Espressif Systems, dan klik **Install**.
3. **Pasang Pustaka (Library) Diperlukan:**
   - Navigasi ke **Tools $\rightarrow$ Manage Libraries...**.
   - Cari dan pasang:
     - `Adafruit PN532` (oleh Adafruit)
     - `Adafruit BusIO` (oleh Adafruit)

---

## ⚠️ Pembetulan Pustaka Penting (Sokongan APDU / HCE)

Dalam `Adafruit_PN532` versi 1.3.4, terdapat pepijat (*bug*) di mana fungsi `inDataExchange()` gagal dilaksanakan selepas `readPassiveTargetID()` kerana indeks sasaran tidak disimpan.

**Lokasi Semakan & Pembetulan:**
Buka fail `/home/<user>/Arduino/libraries/Adafruit_PN532/Adafruit_PN532.cpp` pada baris ~638:

```cpp
  /* Card appears to be Mifare Classic */
  _inListedTag = pn532_packetbuffer[8];  // <--- Pastikan baris ini wujud
  *uidLength = pn532_packetbuffer[12];
```

*Nota: Dalam persekitaran pembangunan repositori ini, pembetulan ini telah disahkan sedia ada.*

---

## ⚙️ Tetapan Wajib Kompilasi Board

Dalam Arduino IDE, pilih port bersiri yang betul dan tetapkan konfigurasi berikut di bawah menu **Tools**:

| Pilihan | Tetapan Diperlukan | Sebab / Kesan Fungsian |
|:--------|:-------------------|:-----------------------|
| **Board** | `ESP32S3 Dev Module` | Menyasarkan mikropengawal dwi-teras Xtensa LX7 |
| **USB CDC On Boot** | **`Enabled`** | **WAJIB.** Menyalurkan komunikasi `Serial` melalui USB Type-C untuk Web Serial API |
| **USB Mode** | `Hardware CDC and JTAG` | Membolehkan USB Serial dan JTAG beroperasi serentak |
| **Upload Speed** | `921600` | Kelajuan muat naik pantas |
| **Flash Mode** | `QIO 80MHz` | Daya pemprosesan memori Quad SPI standard |
| **Partition Scheme** | `Default 4MB with spiffs` | Memuatkan firmware dan timbunan protokol USB |

---

## 🚀 Langkah-Langkah Flashing

1. Sambungkan ESP32-S3 ke komputer anda melalui port USB Type-C asli.
2. Buka fail lakaran `esp32_nfc/esp32_s3_scanner/esp32_s3_scanner.ino`.
3. Pilih port COM yang sepadan (contoh: `/dev/ttyACM0` di Linux, `COMx` di Windows).
4. Klik butang **Upload** (ikon anak panah ke kanan).
5. Buka Serial Monitor pada kelajuan **115200 Baud** untuk mengesahkan output permulaan:
   ```text
   ------------------------------------------------------------------
     Cura. HMS — ESP32-S3 Dual-Mode CUID Engine (HID + WebSerial)    
   ------------------------------------------------------------------
   PN532 Transceiver Online. FW Version: 0x32010607
   ```
6. **AMAT PENTING:** **Tutup Serial Monitor Arduino** sebelum membuka web dashboard Cura. Hanya satu perisian sahaja boleh mengakses port serial pada satu-satu masa.

---

## 🔍 Penyelesaian Masalah Sistem Linux

Jika pelayar web memaparkan ralat *"Connection failed. Ensure the ESP32-S3 is plugged in"* walaupun peranti telah tersenarai:

1. **Periksa Kunci Port (Port Lock):**
   Pastikan tiada aplikasi latar belakang memegang port `/dev/ttyACM0`:
   ```bash
   fuser -v /dev/ttyACM0
   ```
   Jika proses `serial-monitor` disenaraikan, tamatkan proses tersebut atau tutup tetingkap Arduino IDE.

2. **Hentikan Gangguan ModemManager:**
   ModemManager di Linux secara automatik menguji peranti siri CDC:
   ```bash
   echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ENV{ID_MM_DEVICE_IGNORE}="1"' | sudo tee /etc/udev/rules.d/49-esp32.rules
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
