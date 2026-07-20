"""
Script ini dijalankan otomatis tiap hari jam 06:15 WIB oleh GitHub Actions.
Tugasnya:
1. Login pakai akun Telegram kamu (lewat session string, bukan login ulang)
2. Ambil pesan TERAKHIR di chat sama Bot A
3. Kalau pesan itu dokumen CSV -> DOWNLOAD, kompres jadi .zip, kirim ZIP ke Bot B
4. Kalau bukan CSV / gak ada pesan -> skip, gak ngapa-ngapain

KENAPA DI-ZIP (jangan dihapus):
Bot B menerima file lewat Bot API, dan bot Telegram cuma boleh MENGUNDUH file
maksimal 20 MB (batas keras getFile di server Telegram). CSV harian sudah >20 MB,
jadi kalau dokumen aslinya di-forward apa adanya (send_file pakai last_msg.document),
file-nya sampai di Bot B tapi Bot B GAGAL mengunduhnya ("Gagal ambil file").
Akun user (Telethon) tidak kena batas itu — makanya di sini file diunduh dulu lalu
dikompres (CSV biasanya menyusut ~90%, 20 MB -> ~2-3 MB) sebelum dikirim.
Bot B sudah otomatis meng-unzip file .zip yang masuk.

Nama CSV asli dipertahankan sebagai nama file DI DALAM ZIP, karena pipeline Bot B
membaca tanggal snapshot dari nama file itu (sp_golive_odp_report_YYYYMMDD_HHMM.csv).

Semua nilai sensitif diambil dari environment variable (diisi lewat
GitHub Secrets, lihat workflow forward.yml).
"""

import os
import asyncio
import tempfile
import zipfile
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

# Username/ID chat Bot A (sumber CSV) & Bot B (tujuan kirim)
# Contoh: "@nama_bot_a" atau angka chat_id
BOT_A = os.environ["BOT_A_TARGET"]
BOT_B = os.environ["BOT_B_TARGET"]

MB = 1024 * 1024
BOT_API_LIMIT_MB = 20          # batas unduh Bot API di sisi Bot B


async def main():
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        messages = await client.get_messages(BOT_A, limit=1)

        if not messages:
            print("Gak ada pesan sama sekali di chat Bot A. Skip.")
            return

        last_msg = messages[0]

        if not last_msg.document:
            print("Pesan terakhir dari Bot A bukan dokumen. Skip.")
            return

        name = last_msg.file.name or ""
        if not name.lower().endswith(".csv"):
            print(f"Dokumen terakhir ({name or 'tanpa nama'}) bukan CSV. Skip.")
            return

        with tempfile.TemporaryDirectory() as td:
            # 1. Unduh CSV asli (akun user: tanpa batas 20 MB)
            csv_path = await client.download_media(last_msg, file=os.path.join(td, name))
            csv_mb = os.path.getsize(csv_path) / MB

            # 2. Kompres -> .zip (nama CSV asli dipertahankan di dalam ZIP)
            zip_path = os.path.join(td, Path(name).stem + ".zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                zf.write(csv_path, arcname=name)
            zip_mb = os.path.getsize(zip_path) / MB

            if zip_mb > BOT_API_LIMIT_MB:
                print(f"PERINGATAN: ZIP {zip_mb:.1f} MB masih di atas batas unduh Bot API "
                      f"({BOT_API_LIMIT_MB} MB) — Bot B kemungkinan gagal mengunduh.")

            # 3. Kirim ZIP ke Bot B
            await client.send_file(
                BOT_B,
                zip_path,
                caption=f"Auto-forward CSV harian: {name} (ZIP {zip_mb:.1f} MB dari {csv_mb:.1f} MB)",
            )
            print(f"Sukses kirim ZIP '{os.path.basename(zip_path)}' "
                  f"({zip_mb:.1f} MB, asli {csv_mb:.1f} MB) ke {BOT_B}.")


if __name__ == "__main__":
    asyncio.run(main())
