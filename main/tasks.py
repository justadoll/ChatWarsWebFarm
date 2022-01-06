from celery import shared_task
from django.conf import settings
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def make_qr_login():
    client = TelegramClient(StringSession(),api_id=settings.API_ID, api_hash=settings.API_HASH)
    await client.connect()
    qr_login = await client.qr_login()
    settings.QR_LOGIN_TEXT = qr_login.url #global qr_url
    task = asyncio.create_task(qr_login.wait())
    return client,task