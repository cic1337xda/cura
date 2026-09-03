#include <Wire.h>
#include <Adafruit_PN532.h>
#include "USB.h"
#include "USBHIDKeyboard.h"

// Define I2C hardware pins for ESP32-S3
#define SDA_PIN     8
#define SCL_PIN     9

// Assign placeholder GPIO pins for IRQ and RESET
#define PN532_IRQ   4
#define PN532_RESET 5

Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);
USBHIDKeyboard Keyboard;

enum OperationalMode {
  MODE_READ_SCANNER,
  MODE_ARMED_WRITE
};

OperationalMode currentMode = MODE_READ_SCANNER;
uint8_t targetNewUid[4] = {0x00, 0x00, 0x00, 0x00};

void printMenuInstructions() {
  Serial.println("\n------------------------------------------------------------------");
  Serial.println("  Cura. HMS — ESP32-S3 Dual-Mode CUID Engine (HID + WebSerial)    ");
  Serial.println("------------------------------------------------------------------");
}

void setup() {
  // Initialize standard serial and native USB HID
  Serial.begin(115200);
  Keyboard.begin();
  USB.begin();

  delay(2000);
  while (!Serial && millis() < 3000) delay(10);

  printMenuInstructions();

  // Initialize native I2C bus and PN532 peripheral
  Wire.begin(SDA_PIN, SCL_PIN);
  nfc.begin();

  uint32_t fw = nfc.getFirmwareVersion();
  if (!fw) {
    Serial.println("[CRITICAL ERROR] PN532 module not discovered via I2C interface.");
    while (1);
  }

  Serial.print("PN532 Transceiver Online. FW Version: 0x");
  Serial.println(fw, HEX);
  nfc.SAMConfig();
}

void processSerialCommands() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toUpperCase();

    if (input == "READ") {
      currentMode = MODE_READ_SCANNER;
      Serial.println("[SYSTEM STATE] Switched to Standard READ Scanner Mode.");
    }
    else if (input.startsWith("WRITE ") || input.startsWith("W ")) {
      String hexPart = input.substring(input.indexOf(' ') + 1);
      hexPart.trim();

      if (hexPart.length() == 8) {
        unsigned int u[4];
        if (sscanf(hexPart.c_str(), "%02X%02X%02X%02X", &u[0], &u[1], &u[2], &u[3]) == 4) {
          for (int i = 0; i < 4; i++) targetNewUid[i] = (uint8_t)u[i];
          
          currentMode = MODE_ARMED_WRITE;
          Serial.println("[UI_ARMED]"); // Signal for Web Dashboard
          Serial.print("[ARMED] Target UID: ");
          for (int i = 0; i < 4; i++) {
            if (targetNewUid[i] < 0x10) Serial.print("0");
            Serial.print(targetNewUid[i], HEX);
          }
          Serial.println("\n>>> Tap tag/sticker NOW! <<<");
        } else {
          Serial.println("[ERROR] Failed to parse HEX. Use: WRITE A1B2C3D4");
        }
      } else {
        Serial.println("[ERROR] UID must be exactly 8 HEX characters.");
      }
    }
  }
}

// Function to verify if two 4-byte arrays match (Handles reversed order sticker quirk)
bool uidMatches(uint8_t *uid, uint8_t *target) {
  if (uid[0] == target[0] && uid[1] == target[1] && uid[2] == target[2] && uid[3] == target[3]) return true;
  if (uid[0] == target[3] && uid[1] == target[2] && uid[2] == target[1] && uid[3] == target[0]) return true;
  return false;
}

bool performUniversalBlockZeroWrite(uint8_t currentUid[4]) {
  uint8_t defaultKeyA[] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

  if (!nfc.mifareclassic_AuthenticateBlock(currentUid, 4, 0, 0, defaultKeyA)) return false;

  uint8_t blockZeroPayload[16];
  if (!nfc.mifareclassic_ReadDataBlock(0, blockZeroPayload)) memset(blockZeroPayload, 0, 16);

  blockZeroPayload[0] = targetNewUid[0];
  blockZeroPayload[1] = targetNewUid[1];
  blockZeroPayload[2] = targetNewUid[2];
  blockZeroPayload[3] = targetNewUid[3];
  blockZeroPayload[4] = targetNewUid[0] ^ targetNewUid[1] ^ targetNewUid[2] ^ targetNewUid[3];

  if (!nfc.mifareclassic_AuthenticateBlock(currentUid, 4, 0, 0, defaultKeyA)) return false;

  // Execute Gen2 Write
  if (nfc.mifareclassic_WriteDataBlock(0, blockZeroPayload)) {
    delay(50);
    uint8_t newUid[7], newUidLen;
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, newUid, &newUidLen, 500)) {
      if (newUidLen == 4 && uidMatches(newUid, targetNewUid)) {
        Serial.println("[UI_SUCCESS]"); // Signal for Web Dashboard
        return true;
      }
    }
  }

  // Fallback to Gen1a Write
  uint8_t unlock1[] = { 0x40 }, unlock2[] = { 0x43 }, resp[16];
  uint8_t respLen = sizeof(resp);
  nfc.inDataExchange(unlock1, 1, resp, &respLen);
  nfc.inDataExchange(unlock2, 1, resp, &respLen);

  if (!nfc.mifareclassic_AuthenticateBlock(currentUid, 4, 0, 0, defaultKeyA)) return false;
  if (!nfc.mifareclassic_WriteDataBlock(0, blockZeroPayload)) return false;

  delay(50);
  uint8_t newUid2[7], newUidLen2;
  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, newUid2, &newUidLen2, 500)) {
    if (newUidLen2 == 4 && uidMatches(newUid2, targetNewUid)) {
      Serial.println("[UI_SUCCESS]"); // Signal for Web Dashboard
      return true;
    }
  }
  
  Serial.println("[UI_FAILED]"); // Signal for Web Dashboard
  return false;
}

void loop() {
  processSerialCommands();

  uint8_t uid[7];
  uint8_t uidLength;
  bool targetFound = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 200);

  if (targetFound) {
    // Format UID as string
    String uidStr = "";
    for (uint8_t i = 0; i < uidLength; i++) {
      if (uid[i] < 0x10) uidStr += "0";
      uidStr += String(uid[i], HEX);
    }
    uidStr.toUpperCase();

    if (currentMode == MODE_ARMED_WRITE) {
      if (uidLength == 4) {
        bool result = performUniversalBlockZeroWrite(uid);
        if (result) currentMode = MODE_READ_SCANNER;
      } else {
        Serial.println("[UI_FAILED]");
      }
      delay(2500);
    } 
    else if (currentMode == MODE_READ_SCANNER) {
      // 1. Send data to Web Dashboard Widget 1 via WebSerial
      Serial.println("[WEB_READ]:" + uidStr);
      
      // 2. Type data directly into input field via HID Keyboard (Widget 2)
      Keyboard.println(uidStr);
      
      delay(1500); // Cooldown to prevent spam
    }
  }
  delay(50);
}