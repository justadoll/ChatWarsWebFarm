from cmath import log
from django.conf import settings
from .models import CW_players
from .chw_manager import ChwMaster
from telethon import TelegramClient
from telethon.sessions import StringSession
from celery import shared_task
import asyncio

chw_master = ChwMaster(api_id=settings.API_ID, api_hash=settings.API_HASH)
logger = settings.LOGGER


@shared_task
def run_quest_task(p_id, button, after_status):
    logger.debug(f"{after_status=}")
    player = CW_players.objects.get(pk=p_id)
    logger.info(f"[+] {player.chw_username=} {button=}")
    quest_results = asyncio.run(chw_master.mainQuestRun(player,button))
    player.status = after_status
    player.save()
    logger.success(f"{player.chw_username} ended quest!")
    #logger.success(f"{quest_results=}")
    return 0

@shared_task
def def_cow_task(user,pk):
    # TODO collumn in table to check if player already tasked to def-cow (or just status?)
    player = CW_players.objects.get(pk=pk)
    client = TelegramClient(StringSession(player.session),api_id=settings.API_ID, api_hash=settings.API_HASH)
    logger.info(f"[🐮]{user} started def-cow on {player.chw_username}:{player.pk}")
    player.status = "🐮Def-Cow"
    player.save()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(chw_master.def_cow(client))
    except Exception as e:
        logger.error(f"[🐮]{user} have error with def-cow on {player.chw_username}:{player.pk} {e=}")
        return 1
    else:
        logger.success(f"[🐮]{user} finished def-cow on {player.chw_username}:{player.pk}")
    player.status = "🛌Sleep"
    player.save()
    return 0

async def make_qr_login():
    client = TelegramClient(StringSession(),api_id=settings.API_ID, api_hash=settings.API_HASH)
    await client.connect()
    qr_login = await client.qr_login()
    settings.QR_LOGIN_TEXT = qr_login.url #global qr_url
    task = asyncio.create_task(qr_login.wait())
    return client,task