# Cura. HMS — Android Patient Card App

The `cura_app` is a **Flutter (Android)** application that turns a phone into a
digital **NFC patient card** using Android **Host Card Emulation (HCE)**.
Instead of (or alongside) a physical Mifare card, a patient can present their
phone to the clinic's ESP32-S3 reader to be identified instantly.

---

## How it works

1. The user adds patient cards in the app (patient name + 8-char ID, e.g. `C00A0001`).
2. Tapping a card starts an **HCE session** — the app "pretends" to be an NFC tag.
3. The ESP32-S3 reader emits a SELECT APDU for the registered AID.
4. The app replies with the patient ID; the reader types/stores it and the
   dashboard pulls up the matching record.

### HCE contract

| Item | Value |
|------|-------|
| AID | `F222222222` (5 bytes) |
| SELECT APDU | `00 A4 04 00 05 F2 22 22 22 22 00` |
| Success response | `<patient_id UTF-8 bytes> 90 00` |
| File | `android/app/src/main/kotlin/com/example/cura_app/MyHceService.kt` |
| AID registration | `android/app/src/main/res/xml/apduservice.xml` |

### Project layout

```
cura_app/
├── lib/
│   ├── main.dart              # App shell, card store (SharedPreferences), HCE bridge
│   └── widgets/               # GlassCard, GlassDock, DigitalPatientCard
├── android/
│   └── app/src/main/kotlin/.../MyHceService.kt   # HCE APDU processing
│   └── app/src/main/res/xml/apduservice.xml      # AID registration
└── esp32_nfc/esp32_nfc.ino    # Companion scanner sketch (see cura_web/esp32_nfc)
```

The app bridges UI → native HCE through a `MethodChannel`
(`com.example.cura_app/hce`, methods `setPatientId`).

---

## Build & run

```bash
cd cura_app
flutter pub get
flutter run                    # on a connected Android device
```

Requires Android with NFC and HCE support.

---

## Notes & device quirks

- **Android 16+:** `setObserveModeEnabled` is not public on `HostApduService`;
  the code falls back to `NfcAdapter` reflection.
- **Samsung devices:** set the app as the default Tap & Pay service under
  Settings → Connections → NFC → **Tap & Pay** for HCE routing to work.

See the top-level [`known_bugs.md`](../known_bugs.md) for detailed fixes.