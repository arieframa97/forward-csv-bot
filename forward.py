"""
Script ini dijalankan otomatis tiap hari jam 06:15 WIB oleh GitHub Actions.
Tugasnya:
1. Login pakai akun Telegram kamu (lewat session string, bukan login ulang)
2. Ambil pesan TERAKHIR di chat sama Bot A
3. Kalau pesan itu dokumen CSV -> kirim ke Bot B
4. Kalau bukan CSV / gak ada pesan -> skip, gak ngapa-ngapain

Semua nilai sensitif diambil dari environment variable (diisi lewat
GitHub Secrets, lihat workflow forward.yml).
"""

import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

# Username/ID chat Bot A (sumber CSV) & Bot B (tujuan kirim)
# Contoh: "@nama_bot_a" atau angka chat_id
BOT_A = os.environ["BOT_A_TARGET"]
BOT_B = os.environ["BOT_B_TARGET"]


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

        filename = (last_msg.file.name or "").lower()
        if not filename.endswith(".csv"):
            print(f"Dokumen terakhir ({filename or 'tanpa nama'}) bukan CSV. Skip.")
            return

        await client.send_file(
            BOT_B,
            last_msg.document,
            caption=f"Auto-forward CSV harian: {last_msg.file.name}",
        )
        print(f"Sukses kirim '{last_msg.file.name}' ke {BOT_B}.")


if __name__ == "__main__":
    asyncio.run(main())
