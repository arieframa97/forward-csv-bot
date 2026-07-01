# Setup: Auto-forward CSV terakhir dari Bot A ke Bot B

## 0. Apa ini
Tiap hari jam 06:15 WIB, script ini cek pesan terakhir di chat kamu sama
Bot A. Kalau itu file CSV, otomatis dikirim ke Bot B. Jalan gratis pakai
GitHub Actions, gak perlu server.

## 1. Bikin repo GitHub baru — WAJIB PUBLIC
- Public repo = jatah Actions unlimited & gratis (gak makan limit repo lain).
- Upload 3 file ini ke repo:
  - `generate_session.py`
  - `forward.py`
  - `.github/workflows/forward.yml`

## 2. Ambil API_ID & API_HASH
1. Buka https://my.telegram.org, login pakai nomor HP kamu.
2. Masuk "API Development Tools".
3. Bikin aplikasi baru (nama bebas), catat `api_id` dan `api_hash`.

## 3. Generate Session String (di laptop/HP, BUKAN di GitHub)
```
pip install telethon
python generate_session.py
```
Masukkan API_ID, API_HASH, nomor HP, dan kode OTP yang masuk ke Telegram.
Copy "SESSION STRING" yang muncul di akhir. Simpan baik-baik — ini setara
password akun Telegram kamu, jangan dishare ke siapa pun, jangan commit ke repo.

## 4. Masukin semua secret ke GitHub
Repo → Settings → Secrets and variables → Actions → New repository secret.
Bikin 5 secret ini:

| Nama secret      | Isinya                                              |
|-------------------|-----------------------------------------------------|
| `API_ID`          | dari langkah 2                                       |
| `API_HASH`        | dari langkah 2                                       |
| `SESSION_STRING`  | dari langkah 3                                       |
| `BOT_A_TARGET`    | username Bot A, contoh `@nama_bot_a`                 |
| `BOT_B_TARGET`    | username Bot B, contoh `@nama_bot_b`                 |

> Catatan: akun Telegram kamu (yang dipakai login) harus SUDAH PERNAH chat
> sama Bot B minimal sekali (pencet /start), kalau belum, bot gak akan mau
> nerima pesan dari kamu.

## 5. Tes manual dulu sebelum nunggu besok pagi
Repo → tab "Actions" → pilih workflow "Forward CSV Bot A ke Bot B" →
"Run workflow" → klik tombol hijau. Cek log-nya, harusnya muncul
"Sukses kirim '...' ke @nama_bot_b."

## 6. Selesai
Mulai besok, script jalan otomatis tiap jam 06:15 WIB.

## Catatan jujur soal keterbatasan
- Jadwal cron GitHub Actions kadang meleset beberapa menit (bukan presisi
  detik), terutama pas jam-jam sibuk global. Wajar, bukan bug.
- Kalau Bot A belum pernah kirim CSV apa pun di chat, atau pesan terakhir
  bukan CSV, script cuma skip — gak error, gak ngirim apa-apa.
- Akun Telegram kamu yang "meminjamkan" akses baca chat Bot A — pastikan
  akun itu memang yang biasa kamu pakai buat terima CSV dari Bot A.
