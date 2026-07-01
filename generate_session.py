"""
JALANKAN INI SEKALI AJA DI LAPTOP/HP KAMU (bukan di GitHub Actions).
Tujuannya: login pakai akun Telegram kamu, terus keluarin "session string"
yang dipakai script forward.py nanti (jadi gak perlu login ulang tiap hari).

Cara pakai:
1. pip install telethon
2. Ambil API_ID & API_HASH di https://my.telegram.org -> API Development Tools
3. python generate_session.py
4. Masukkan API_ID, API_HASH, nomor HP, kode OTP yang masuk ke Telegram
5. Copy SESSION STRING yang muncul -> simpan, JANGAN dishare ke siapa pun
   (itu setara password akun Telegram kamu)
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("API_ID: ").strip())
api_hash = input("API_HASH: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n=== SESSION STRING (simpan baik-baik, JANGAN dibagikan) ===\n")
    print(client.session.save())
    print("\n=============================================================")
