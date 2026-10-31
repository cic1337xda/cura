# 🔒 Spesifikasi Keselamatan, Kriptografi & Seni Bina

> Huraian teknikal terperinci mengenai pelaksanaan kriptografi, jangka hayat pengesahan sesi, algoritma penjanaan ID deterministik, dan middleware keselamatan.

## 📑 Pilihan Bahasa / Language Options
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](SECURITY_AND_ARCHITECTURE_MY.md)**
* 🇬🇧 **[English Documentation](SECURITY_AND_ARCHITECTURE.md)**

---

## 🛡️ 1. Pengesahan Pengguna & Jangka Hayat Sesi

1. **Hashing Kata Laluan:**
   - Kata laluan untuk pentadbir dan doktor di-hash menggunakan **Bcrypt** dengan salt dijana secara rawak melalui `passlib.context.CryptContext`.
   - Kata laluan teks biasa (*plaintext*) tidak pernah disimpan atau direkod dalam log pelayan.
2. **Token Sesi JWT Tanpa Keadaan (Stateless):**
   - Sesi disahkan menggunakan JSON Web Tokens (JWT) yang ditandatangani secara kriptografi dengan **HMAC-SHA256 (`HS256`)**.
   - Tuntutan (*claims*) dalam token mengandungi:
     - `sub`: Pengenal unik pengguna
     - `role`: Skop kebenaran capaian (`admin` atau `doctor`)
     - `doc_number`: Nombor staf doktor (jika peranan adalah doktor)
     - `exp`: Cap masa tamat tempoh sesi (Lalai: 480 minit / 8 jam)

---

## 🚦 2. Middleware Keselamatan & Penjejakan Permintaan

Didaftarkan dalam `app/core/middleware.py`, middleware `SecurityAndTracingMiddleware` menapis setiap permintaan HTTP yang masuk:

1. **Penjejakan Permintaan (`X-Request-ID`):**
   - Menjana `UUID4` unik untuk setiap permintaan HTTP (atau mengekalkan ID korelasi pelanggan sedia ada).
   - Diselitkan ke dalam header respons `X-Request-ID` bagi memudahkan penjejakan ralat dalam log proksi reverse.
2. **Pertahanan Clickjacking:**
   - Menyuntik header `X-Frame-Options: DENY`, menghalang dashboard daripada disematkan dalam tag berniat jahat seperti `<iframe>` atau `<embed>`.
3. **Pencegahan Penghiduan MIME (MIME Sniffing):**
   - Menyuntik header `X-Content-Type-Options: nosniff` untuk memaksa pelayar mematuhi Content-Type yang diisytiharkan oleh pelayan.
4. **Dasar Perujuk (Referrer Policy):**
   - Menyuntik `Referrer-Policy: strict-origin-when-cross-origin` bagi mengelakkan kebocoran maklumat laluan URL kepada domain luar.

---

## 🔢 3. Penjanaan ID Bersiri Deterministik

Semua entiti hospital mengelakkan pendedahan nombor integer auto-increment biasa. Sebaliknya, penjana ID berpusat (`app/core/idgen.py`) memperuntukkan **awalan HEX 4-aksara + nombor 4-digit berbantalan sifar** (`C##A####`).

```text
[ AWALAN ]  [ AKHIRAN ANGKA ]
  C00A            0001         =  C00A0001 (Rentetan HEX 8-aksara)
```

### Matriks Awalan Entiti:
* `C00A`: Pesakit
* `C01A`: Doktor / Pengamal Perubatan
* `C02A`: Preskripsi Ubat
* `C03A`: Ujian Makmal
* `C04A`: Bacaan Tanda Vital
* `C05A`: Rekod Perubatan Klinikal
* `C06A`: Jadual Dewan Bedah
* `C07A`: Pembekal & Vendor
* `C08A`: Akaun (Boleh Bayar / Boleh Terima)
* `C09A`: Penggajian Staf

### Mengapa Format HEX 8-Aksara?
Kad pintar NFC Mifare Classic mempunyai Blok 0 (UID pengilang) bersaiz **tepat 4 bait (32 bit)**, yang diwakili dalam format heksadesimal sebagai 8 aksara (`0x00` - `0xFF` x 4). Dengan memformatkan ID kepada `C00A0001`, pengenal pangkalan data hospital boleh dipetakan terus ke dalam cip perkakasan fizikal tanpa memerlukan jadual pemetaan kedua.

---

## 🪪 4. Keselamatan Kad Pintar Dwi-Mod & MyKad

1. **Sokongan MyKad Malaysia (`ic_card_uid`):**
   - Kad MyKad fizikal mengandungi cip tanpa sentuh. Pengimbas membaca UID perkakasan cip tanpa enkripsi (contoh: `CF289949`).
   - UID cip ini dijadikan petunjuk indeks identiti pesakit, manakala maklumat biometrik dan butiran sulit lain kekal selamat di dalam pangkalan data hospital yang disulitkan.
2. **Keselamatan Kad Magik CUID Blok 0:**
   - Kad Mifare standard mengunci Blok 0 secara kekal dari kilang. Penulisan ke Blok 0 memerlukan kad CUID Gen2 atau Gen1a khas.
   - Firmware melaksanakan jujukan pengesahan dwi-kunci (`defaultKeyA: 0xFF...FF`) dan mengesahkan blok yang ditulis sebelum menghantar isyarat `[UI_SUCCESS]` ke web dashboard.

---

## 📜 Lesen
* Dibangunkan untuk **Tujuan Pembelajaran Sahaja** (Educational Purposes Only).
