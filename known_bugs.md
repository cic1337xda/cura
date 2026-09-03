# Known Bugs & Fixes — Cura. HMS

## 1. PN532 `inDataExchange` Always Fails After `readPassiveTargetID()`

**Symptom:**
- ESP32/PN532 detects Android HCE target (UID starting with `08`)
- `inDataExchange()` always returns `false` — no APDU response
- Android logcat never shows "APDU received"

**Root Cause:**
Adafruit_PN532 library v1.3.4, `Adafruit_PN532.cpp` — `readDetectedPassiveTargetID()` (called by `readPassiveTargetID()`) reads the target number from the PN532 response buffer at `pn532_packetbuffer[8]` but NEVER stores it in the class member `_inListedTag`.

`inDataExchange()` uses `_inListedTag` as the target number when sending the PN532 `InDataExchange` command (line 679: `pn532_packetbuffer[1] = _inListedTag;`). Since `_inListedTag` stays at `0` (uninitialized), the PN532 receives target number `0` which doesn't exist — only target `1` exists. Every APDU exchange times out.

Note: `inListPassiveTarget()` DOES set `_inListedTag` (line 794), which is why that function works but `readPassiveTargetID()` doesn't.

**Fix:**
Edit `/home/cic1337xda/Arduino/libraries/Adafruit_PN532/Adafruit_PN532.cpp`, line ~638.

Before:
```cpp
  /* Card appears to be Mifare Classic */
  *uidLength = pn532_packetbuffer[12];
```

After:
```cpp
  /* Card appears to be Mifare Classic */
  _inListedTag = pn532_packetbuffer[8];
  *uidLength = pn532_packetbuffer[12];
```

**File:** `android/app/src/main/kotlin/com/example/cura_app/MyHceService.kt`

---

## 2. `setObserveModeEnabled` Not Found on `HostApduService` (Android 16)

**Symptom:**
- Logcat: `setObserveModeEnabled not found on HostApduService`
- But: `Observe mode disabled via NfcAdapter` — fallback works

**Root Cause:**
On Android 16 (API 36), the hidden method `setObserveModeEnabled` is not a public method on `HostApduService`. `getMethod()` only finds public methods, so it throws `NoSuchMethodException`.

**Fix:**
The fallback in `MyHceService.kt` uses `getDeclaredMethod` on `NfcAdapter` which works. If this ever breaks too, add more fallback approaches or remove the reflection entirely — newer Android versions may change observe mode defaults.

---

## 3. Samsung Devices Require Default Payment App for HCE

**Symptom:**
- `setPreferredService result: false` in logcat
- Phone not detected by NFC reader at all

**Fix:**
On Samsung devices (S23 Ultra, etc.):  
Settings → Connections → NFC and contactless payments → Tap & Pay → Select "cura_app" as default.

Without this, Samsung's One UI NFC stack may ignore `setPreferredService()` calls from non-payment apps.

---

## Key Files

| File | Purpose |
|------|---------|
| `MyHceService.kt` | HCE APDU processing, observe mode disable |
| `MainActivity.kt` | NFC adapter init, preferred service, Platform Channel |
| `apduservice.xml` | AID registration (`F222222222`), HCE service declaration |
| `AndroidManifest.xml` | Permissions, service/intent-filter, meta-data |
| `esp32_nfc.ino` | PN532 reader + APDU exchange with Android HCE |

## AID Reference

| Component | AID |
|-----------|-----|
| `apduservice.xml` | `F222222222` |
| ESP32 SELECT APDU | `00 A4 04 00 05 F2 22 22 22 22 00` |
| MyHceService.kt check | Matches bytes `F2 22 22 22 22` at positions 5-9 |

## APDU Response Format

SELECT AID response: `<patientId as UTF-8 bytes>` + `90 00`
- `patientId` example: `"383838183"` → bytes: `33 38 33 38 33 38 31 38 33`
- Status word: `90 00` (success)
- Full response example: `33 38 33 38 33 38 31 38 33 90 00`

---

## 4. Card Write Can Fail ("[UI_FAILED]")

**Symptom:**
- `Write Card` in the dashboard sends `WRITE C00A0001`, the reader arms, but the
  card reports `[UI_FAILED]` (or success is never confirmed).

**Root Causes (in order of likelihood):**

1. **Wrong card type.** Only **CUID / Magic** Mifare Classic cards allow Block 0
   rewriting. Standard Mifare (including NDEF-formatted tags) locks Block 0 by
   the manufacturer — the firmware then reports `[UI_FAILED]`.
2. **Card removed too early.** The re-read verification after writing is skipped
   if the card is pulled before `delay(50)` + `readPassiveTargetID(500ms)` completes.
3. **Card already locked.** Some CUID cards can be permanently locked after the
   first write (U-Lock). Try a fresh card.
4. **Authenticated read of Block 0 fails** → `mifareclassic_ReadDataBlock(0)` returns
   false, so a zeroed payload is written instead of the original header/checksum.

**Fix / verification (serial terminal):**
```bash
WRITE A1B2C3D4      # expect [UI_ARMED], then tap the card → [UI_SUCCESS]
READ
# tap again → expect [WEB_READ]:A1B2C3D4 (or reversed A4D3C2B1 for sticker quirk)
```

The firmware intentionally handles the **reversed-order sticker** quirk in
`uidMatches()` (physical stickers often print/route bytes reversed).
