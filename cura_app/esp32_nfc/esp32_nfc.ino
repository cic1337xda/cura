#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_SS   5

Adafruit_PN532 nfc(PN532_SS);

void setup() {
  Serial.begin(115200);
  delay(2000);
  while (!Serial) delay(10);

  Serial.println();
  Serial.println("=====================================================");
  Serial.println("   Cura. HMS - PN532 HCE Reader (Fixed Library)      ");
  Serial.println("=====================================================");

  nfc.begin();
  uint32_t fw = nfc.getFirmwareVersion();
  if (!fw) {
    Serial.println("[CRITICAL] PN532 not found.");
    while (1);
  }
  Serial.print("PN532 Firmware: 0x");
  Serial.println(fw, HEX);

  nfc.SAMConfig();
  Serial.println("Ready. Hold phone near PN532 antenna.");
}

void loop() {
  uint8_t uid[7];
  uint8_t uidLength;

  bool found = nfc.readPassiveTargetID(
                  PN532_MIFARE_ISO14443A,
                  uid, &uidLength, 1000);

  if (found) {
    Serial.print("\n[FOUND] UID: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      if (uid[i] < 0x10) Serial.print("0");
      Serial.print(uid[i], HEX);
    }
    Serial.println();

    delay(300);

    uint8_t selectAid[] = {
      0x00, 0xA4, 0x04, 0x00,
      0x05,
      0xF2, 0x22, 0x22, 0x22, 0x22,
      0x00
    };
    uint8_t resp[64];
    uint8_t respLen = sizeof(resp);

    bool ok = nfc.inDataExchange(selectAid, sizeof(selectAid), resp, &respLen);

    if (ok && respLen >= 2) {
      uint8_t sw1 = resp[respLen - 2];
      uint8_t sw2 = resp[respLen - 1];

      Serial.print("Response: ");
      for (uint8_t i = 0; i < respLen; i++) {
        if (resp[i] < 0x10) Serial.print("0");
        Serial.print(resp[i], HEX);
        Serial.print(" ");
      }
      Serial.println();

      if (sw1 == 0x90 && sw2 == 0x00) {
        int pl = respLen - 2;
        char buf[pl + 1];
        memcpy(buf, resp, pl);
        buf[pl] = '\0';
        Serial.println("================================================================");
        Serial.print(">>> HCE TOKEN: ");
        Serial.println(buf);
        Serial.println("================================================================");
        delay(3000);
        return;
      } else {
        Serial.print("[REJECTED] SW=");
        Serial.print(sw1, HEX);
        Serial.print(sw2, HEX);
        Serial.println();
      }
    } else {
      Serial.println("[FAIL] No APDU response.");
    }

    delay(2000);
  }

  delay(100);
}