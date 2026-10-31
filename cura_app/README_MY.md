# Cura. HMS — Aplikasi Kad Pesakit Android (HCE)

Aplikasi `cura_app` ialah aplikasi **Flutter (Android)** yang menukar telefon pintar menjadi
**kad pesakit NFC digital** menggunakan teknologi **Host Card Emulation (HCE)** Android.
Selain daripada kad fizikal Mifare/CUID, pesakit boleh merapatkan telefon pintar mereka ke
pengimbas ESP32-S3 di kaunter untuk pengecaman rekod secara serta-merta.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](README_MY.md)**
* 🇬🇧 **[English Documentation](README.md)**

---

## 🧭 Cara Sistem Beroperasi

1. Pengguna mendaftarkan profil kad pesakit di dalam aplikasi (Nama + 8-aksara ID, contoh: `C00A0001`).
2. Menekan kad akan memulakan **sesi HCE** — telefon bertindak seolah-olah cip kad NFC pasif.
3. Pengimbas kaunter ESP32-S3 menghantar arahan APDU `SELECT AID` untuk AID yang berdaftar.
4. Aplikasi membalas dengan ID pesakit; pengimbas menangkap data tersebut dan web dashboard membuka rekod pesakit serta-merta.

### Kontrak Komunikasi HCE

| Perkara | Nilai Spesifikasi |
|:--------|:------------------|
| AID Berdaftar | `F222222222` (5 bait) |
| Arahan APDU SELECT | `00 A4 04 00 05 F2 22 22 22 22 00` |
| Respons Kejayaan | `<bait UTF-8 ID pesakit> 90 00` |
| Kod Sumber HCE | `android/app/src/main/kotlin/com/example/cura_app/MyHceService.kt` |
| Pendaftaran AID | `android/app/src/main/res/xml/apduservice.xml` |

### Susun Atur Projek

```text
cura_app/
├── lib/
│   ├── main.dart              # Titik masuk aplikasi, storan kad (SharedPreferences) & jambatan HCE
│   └── widgets/               # Widget GlassCard, GlassDock, DigitalPatientCard
├── android/
│   └── app/src/main/kotlin/.../MyHceService.kt   # Pemprosesan APDU HCE asli
│   └── app/src/main/res/xml/apduservice.xml      # Pendaftaran AID perkhidmatan HCE
└── esp32_nfc/esp32_nfc.ino    # Lakaran pengimbas pendamping
```

Aplikasi menghubungkan antaramuka Flutter $\rightarrow$ perkhidmatan HCE asli melalui `MethodChannel`
(`com.example.cura_app/hce`, kaedah `setPatientId`).

---

## ⚡ Bina & Jalankan

```bash
cd cura_app
flutter pub get
flutter run                    # pada peranti Android yang disambungkan
```

Memerlukan peranti Android dengan sokongan perkakasan NFC dan HCE.

---

## ⚠️ Nota & Ciri Khas Peranti

- **Android 16+:** Kaedah `setObserveModeEnabled` bukan kaedah awam pada `HostApduService`; kod mempunyai *fallback* pantulan ke `NfcAdapter`.
- **Peranti Samsung:** Aplikasi mesti ditetapkan sebagai perkhidmatan pembayaran piawai di bawah
  **Settings $\rightarrow$ Connections $\rightarrow$ NFC $\rightarrow$ Tap & Pay** untuk penghalaan HCE berfungsi.

Sila rujuk fail [`known_bugs.md`](../known_bugs.md) untuk perincian penyelesaian masalah.

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
