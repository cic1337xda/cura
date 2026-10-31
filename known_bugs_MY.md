# Senarai Pepijat Diketahui & Penyelesaian — Cura. HMS

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](known_bugs_MY.md)**
* 🇬🇧 **[English Documentation](known_bugs.md)**

---

## 1. Kegagalan Fungsi `inDataExchange` PN532 Selepas `readPassiveTargetID()`

**Gejala:**
- Pengimbas ESP32/PN532 berjaya mengesan sasaran Android HCE (UID bermula `08`).
- Fungsi `inDataExchange()` sentiasa memulangkan nilai `false` — tiada respons APDU diterima.
- Logcat Android tidak menunjukkan sebarang mesej "APDU received".

**Punca Utama:**
Pustaka Adafruit_PN532 v1.3.4, fail `Adafruit_PN532.cpp` — fungsi `readDetectedPassiveTargetID()` membaca nombor sasaran daripada penimbal respons PN532 pada `pn532_packetbuffer[8]` tetapi tidak menyimpannya ke dalam pembolehubah kelas `_inListedTag`.

`inDataExchange()` memerlukan `_inListedTag` sebagai nombor sasaran. Oleh kerana nilainya kekal `0`, modul PN532 menerima arahan untuk sasaran 0 yang tidak wujud.

**Penyelesaian:**
Buka fail `/home/<user>/Arduino/libraries/Adafruit_PN532/Adafruit_PN532.cpp` pada baris ~638:

```cpp
  /* Card appears to be Mifare Classic */
  _inListedTag = pn532_packetbuffer[8];  // <--- Tambah baris ini
  *uidLength = pn532_packetbuffer[12];
```

---

## 2. Ralat `setObserveModeEnabled` Tidak Ditemui pada `HostApduService` (Android 16)

**Gejala:**
- Logcat: `setObserveModeEnabled not found on HostApduService`.
- Tetapi sistem tetap berfungsi melalui pantulan: `Observe mode disabled via NfcAdapter`.

**Punca:**
Pada Android 16 (API 36), kaedah `setObserveModeEnabled` bukan kaedah awam pada `HostApduService`.

**Penyelesaian:**
Kaedah alternatif (*fallback*) dalam `MyHceService.kt` menggunakan `getDeclaredMethod` pada kelas `NfcAdapter` yang disokong dengan stabil.

---

## 3. Peranti Samsung Memerlukan Pilihan Aplikasi Pembayaran Default

**Gejala:**
- Logcat menunjukkan `setPreferredService result: false`.
- Telefon pintar tidak dapat dikesan oleh pengimbas NFC kaunter.

**Penyelesaian:**
Pada telefon pintar Samsung (siri Galaxy S23, dll):  
**Settings $\rightarrow$ Connections $\rightarrow$ NFC and contactless payments $\rightarrow$ Tap & Pay $\rightarrow$ Pilih "cura_app" sebagai default.**

---

## 4. Kegagalan Menulis Kad Fizikal ("[UI_FAILED]")

**Gejala:**
- Butang `Write Card` di dashboard menghantar arahan `WRITE C00A0001`, pengimbas bersedia (*armed*), tetapi sistem memaparkan amaran `[UI_FAILED]`.

**Punca-Punca Utama:**
1. **Jenis Kad Salah:** Hanya kad **CUID / Magic** Mifare Classic membenarkan penulisan semula Blok 0. Kad standard Mifare mempunyai Blok 0 yang dikunci kekal dari kilang.
2. **Kad Dialihkan Terlalu Awal:** Kad diangkat sebelum proses pengesahan bacaan selesai.
3. **Kad Terkunci:** Sesetengah kad CUID terkunci secara kekal selepas penulisan pertama. Gunakan kad baharu.

---

## 5. Pelayar Web Telefon Tidak Boleh Mengimbas Kad Emulasi HCE (Had API Web NFC)

**Gejala:**
- Telefon Android boleh mengimbas kad fizikal melalui Web NFC pelayar Chrome.
- Tetapi apabila telefon cuba mengimbas kad emulasi `cura_app` dari telefon lain, paparan ralat terhasil.
- Kad emulasi yang sama boleh dibaca dengan lancar oleh pengimbas kaunter ESP32-S3 / PN532.

**Punca:**
Standard API **Web NFC (`NDEFReader`)** di pelayar web hanya direka untuk membaca tag fizikal berformat NDEF. Ia tidak menyokong pertukaran arahan APDU ISO-DEP peringkat rendah yang diperlukan oleh perkhidmatan emulasi Android HCE.

| Pengimbas | Kad Fizikal | Telefon HCE (cura_app) |
|:----------|:-----------:|:----------------------:|
| Web NFC Telefon | ✅ | ❌ |
| ESP32-S3 / PN532 | ✅ | ✅ |

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
