# Cura. HMS ESP32-S3 NFC Firmware

This folder contains the firmware for the ESP32-S3 microcontroller to interface with the PN532 NFC module. 

## Features
- **Dual-Mode Operation:** Functions simultaneously as a USB HID Keyboard (for typing UIDs anywhere) and as a Web Serial endpoint (for direct integration with the Cura. HMS dashboard).
- **Read & Write:** Capable of reading physical NFC cards and writing 8-character HEX IDs to **Mifare Classic CUID Gen2** (and Gen1a fallback) cards.
- **Web Serial Protocol:** Emits structured payloads (`[WEB_READ]:<uid>`, `[UI_SUCCESS]`, `[UI_FAILED]`) consumed directly by the browser via the Web Serial API.

## Hardware Setup
This firmware uses the ESP32-S3 native USB for both Serial and HID.

### Wiring (I2C)
Ensure your PN532 module's DIP switches are configured for **I2C mode**.

| PN532 Pin | ESP32-S3 Pin |
|-----------|--------------|
| SDA       | GPIO 8       |
| SCL       | GPIO 9       |
| IRQ       | GPIO 4       |
| RESET     | GPIO 5       |
| VCC       | 3.3V or 5V   |
| GND       | GND          |

## Dependencies
Install the following libraries in your Arduino IDE:
1. `Adafruit PN532`
2. `Adafruit BusIO`

## Uploading via Arduino IDE
1. Go to **Tools -> Board** and select `ESP32S3 Dev Module`.
2. Ensure **USB CDC On Boot** is set to `Enabled` (Required for Web Serial).
3. Ensure **USB Mode** is set to `Hardware CDC and JTAG`.
4. Compile and upload.

## Note on Writing Cards
The firmware writes the patient ID (e.g., `C00A0001`) into **Block 0** of the Mifare card. This requires special "Magic" CUID cards where Block 0 is writable. Standard Mifare cards cannot be reprogrammed in this way.