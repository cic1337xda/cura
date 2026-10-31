# ⚡ Firmware Toolchain Setup & Flashing Guide

> Step-by-step instructions for compiling and uploading the dual-mode CUID & HCE scanner firmware to the ESP32-S3 microcontroller.

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](FLASHING_AND_SETUP.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](FLASHING_AND_SETUP_MY.md)**

---

## 🛠️ Prerequisites & Arduino IDE Setup

1. **Install Arduino IDE:** Download version 2.x from [arduino.cc](https://www.arduino.cc/en/software).
2. **Add ESP32 Board Support:**
   - Go to **File $\rightarrow$ Preferences $\rightarrow$ Additional Board Manager URLs**.
   - Add: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - Open **Tools $\rightarrow$ Board $\rightarrow$ Boards Manager**, search for `esp32` by Espressif Systems, and click **Install** (version 2.0.x or 3.0.x).
3. **Install Required Libraries:**
   - In Arduino IDE, navigate to **Tools $\rightarrow$ Manage Libraries...**.
   - Search for and install:
     - `Adafruit PN532` (by Adafruit)
     - `Adafruit BusIO` (by Adafruit)

---

## ⚠️ Critical Library Fix (APDU / HCE Support)

In `Adafruit_PN532` version 1.3.4, a known bug prevents `inDataExchange()` from executing after `readPassiveTargetID()` because the target index is not preserved.

**Verification / Patch Location:**
Open `/home/<user>/Arduino/libraries/Adafruit_PN532/Adafruit_PN532.cpp` around line 638:

```cpp
  /* Card appears to be Mifare Classic */
  _inListedTag = pn532_packetbuffer[8];  // <--- Ensure this line is present
  *uidLength = pn532_packetbuffer[12];
```

*Note: On this repository development environment, this patch has already been verified.*

---

## ⚙️ Mandatory Board Compilation Settings

In Arduino IDE, select the target port and configure the following parameters under the **Tools** menu:

| Option | Required Setting | Reason / Impact |
|:-------|:-----------------|:----------------|
| **Board** | `ESP32S3 Dev Module` | Targets the dual-core Xtensa LX7 MCU architecture |
| **USB CDC On Boot** | **`Enabled`** | **MANDATORY.** Directs `Serial` over native USB Type-C for Web Serial API |
| **USB Mode** | `Hardware CDC and JTAG` | Enables concurrent USB Serial and JTAG debugging |
| **Upload Speed** | `921600` | High-speed flashing |
| **Flash Mode** | `QIO 80MHz` | Standard Quad SPI flash throughput |
| **Partition Scheme** | `Default 4MB with spiffs` | Accommodates core firmware and USB stacks |

---

## 🚀 Flashing Steps

1. Connect the ESP32-S3 to your workstation via the native USB port.
2. Open `esp32_nfc/esp32_s3_scanner/esp32_s3_scanner.ino`.
3. Select your serial port (e.g. `/dev/ttyACM0` on Linux, `COMx` on Windows).
4. Click **Upload** (arrow icon).
5. Open the Arduino Serial Monitor at **115200 Baud** to verify the boot message:
   ```text
   ------------------------------------------------------------------
     Cura. HMS — ESP32-S3 Dual-Mode CUID Engine (HID + WebSerial)    
   ------------------------------------------------------------------
   PN532 Transceiver Online. FW Version: 0x32010607
   ```
6. **IMPORTANT:** **Close the Arduino Serial Monitor** before connecting to the Cura web dashboard. Only one application can access the serial port at any given time.

---

## 🔍 Linux Workstation Troubleshooting

If the browser reports *"Connection failed. Ensure the ESP32-S3 is plugged in"* despite showing as paired:

1. **Check for Port Lock:**
   Verify whether another background process has grabbed `/dev/ttyACM0`:
   ```bash
   fuser -v /dev/ttyACM0
   ```
   If `serial-monitor` or `minicom` is listed, terminate it or close the Arduino IDE window.

2. **Disable ModemManager Interference:**
   ModemManager automatically probes CDC serial devices on Linux:
   ```bash
   echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ENV{ID_MM_DEVICE_IGNORE}="1"' | sudo tee /etc/udev/rules.d/49-esp32.rules
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

---

## 📜 License
* Developed for **Educational Purposes Only**.
