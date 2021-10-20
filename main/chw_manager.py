from telethon.sync import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession

from main.models import CW_players
from loguru import logger
import asyncio
from emoji import emojize
import re

class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

defence = emojize(":shield:Защита")
hero = emojize(":sports_medal:Герой")
quests = emojize("🗺Квесты")
castle = emojize("🏰Замок")

# Telethon funcions
async def client_init(sess_str):
    client = TelegramClient(StringSession(sess_str), 2299164, "c8b6a3a2edaae9f1d98a2c5596457dce")
    #try:
    #player = CW_players.objects.get(pk=11)
    #logger.debug(player.username)
    await client.connect()
    return client

async def chw_get_msg(client,mode):
    await client.send_message('ChatWarsBot', mode)
    await asyncio.sleep(1.5)
    msg = await client.get_messages("ChatWarsBot")
    return msg

async def get_user_data(sessionFromRequest):
    client = await client_init(sessionFromRequest)
    info = await client(GetFullUserRequest('me'))
    logger.info(info.user.id)
    username = info.user.username
    await client.disconnect()
    return username

# Game Functions
async def mainQuestRun(player_obj,quest_range):
    client = await client_init(player_obj.session)
    logger.debug(f"[+] {player_obj.chw_username} started!")
    lvl = await hero_level(client)
    cast_range = AsyncIterator(range(quest_range))
    async for i in cast_range:
        await quest_auto(client, lvl)

    await asyncio.sleep(3)
    await client.disconnect()
    logger.debug(f"[-] {player_obj.chw_username} disconnected")

async def quest_auto(cli, lvl):
    """ Function that go client to quiest while have stamina """
    info = await cli(GetFullUserRequest('me'))
    stam = await hero_stamina(cli)
    logger.debug("Stamina: "+str(stam))
    if stam > 0:
        logger.info(f"{info.user.username} have stamina, have we go!")
        await cli.send_message("ChatWarsBot", quests)
        await asyncio.sleep(1)
        msg1 = await cli.get_messages("ChatWarsBot")
        if lvl >= 20:
            button = await get_game_time(cli)
        #elif lvl >= 20 and is_knight
        elif lvl < 20:
            logger.debug("LowLevel: Forest!")
            button = 0

        if await msg1[0].click(button) == None:
            logger.error("Click failed")
            await quest_auto(cli,lvl)
        else:
            await asyncio.sleep(1)
            msg_time = await cli.get_messages("ChatWarsBot")
            #logger.debug("Message:"+msg_time[0].message)
            msg_time = re.findall("\d+", str(msg_time[0].text))
            try:
                msg_time = str(msg_time[0])
                msg_time = int(msg_time)
                msg_time *= 60
                logger.info("Time in quest: "+str(msg_time))
                msg_time += 20
                await asyncio.sleep(msg_time)
                return True
            except Exception:
                logger.error("Something gone wrong!")

    else:
        await asyncio.sleep(3)
        logger.debug("No stamina! Return False")
        #await cli.send_message("ChatWarsBot", defence)
        #return None?
        #await asyncio.sleep(3)
        return False

# sub funcs TODO Class with init and rename of cli or something else
async def get_game_time(player_obj):
    """ Check and game time"""
    if (type(player_obj) == CW_players):
        client = await client_init(player_obj.session)
    else:
        client = player_obj
        logger.debug(f"Client was inited! His type is: {str(type(client))}!")
    msg = await chw_get_msg(client, castle)
    msg = str(msg[0].message)
    spl = msg.split("\n")
    r = re.findall("\w+",spl[1])
    if(r[0] == "Утро"):
        logger.debug("Mountains!")
        return 2
    elif(r[0] == "День"):
        logger.debug("Forest!")
        return 0
    else:
        logger.debug("Swamp!")
        return 1

async def hero_level(cli):
    msg = await chw_get_msg(cli,hero)
    msg = str(msg[0].message)
    rd = re.findall("Уровень: \d+", msg)
    rs = int(re.findall("\d+",rd[0])[0])
    logger.debug("LVL "+str(rs))
    return rs

async def hero_stamina(client):
    """ Check how many stamina client have  """
    #client = await client_init(sessionFromRequest)
    msg = await chw_get_msg(client,hero)
    msg = str(msg[0].message)
    stamina = re.findall("Выносливость: \d+\/\d+", msg)
    stamina = re.findall("\d", stamina[0])
    stamina = int(stamina[0])
    return stamina
