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

# Game funcions
class ChwMaster():
    def __init__(self, api_id, api_hash):
        """ Initilize service """
        self.api_id = api_id
        self.api_hash = api_hash
        # Stikers
        self.defence = emojize(":shield:Защита")
        self.hero = emojize(":sports_medal:Герой")
        self.quests = emojize("🗺Квесты")
        self.castle = emojize("🏰Замок")
        # Poisons before quests
        self.quest_poisons = {"Greed":[{"VOG":"/use_p07"},{"POG":"/use_p08"},{"BOG":"/use_p09"}],
                "Nature":[{"VON":"/use_p10"},{"PON":"/use_p11"},{"BON":"/use_p12"}]
                }
        # Poisons before battle 
        self.battle_poisons = {"Rage":[{"VOR":"/use_p01"},{"POR":"/use_p02"}, {"BOR":"/use_p03"}],
                "Peace":[{"VOP":"/use_p04"},{"POP":"/use_p05"},{"BOP":"/use_p06"}]
                }

    async def client_init(self, sess_str):
        client = TelegramClient(StringSession(sess_str), self.api_id, self.api_hash)
        #try:
        await client.connect()
        return client

    async def chw_get_msg(self, client,mode):
        await client.send_message('ChatWarsBot', mode)
        await asyncio.sleep(1.5)
        msg = await client.get_messages("ChatWarsBot")
        return msg

    async def get_user_data(self, player_obj):
        if (type(player_obj) == CW_players):
            client = await self.client_init(player_obj.session)
        else:
            client = player_obj
            logger.debug(f"Client was inited! His type is: {str(type(client))}!")
        info = await client(GetFullUserRequest('me'))
        logger.info(info.user.id)
        username = info.user.username
        await client.disconnect()
        return username

    async def get_player_info(self, player_obj):
        results = {}
        client = await self.client_init(player_obj.session)
        res = await self.chw_get_msg(client, self.hero)
        full_msg = res[0].message
        if "🌟Поздравляем! Новый уровень!🌟" in full_msg:
            logger.debug("LVLUP!")
            results["lvlup"] = True
        rd = re.findall("Уровень: \d+", full_msg)
        lvl = int(re.findall("\d+",rd[0])[0])
        results['lvl'] = lvl

        state = re.findall('Состояние:\n[🛌🛡⚔🔎🐫📯🌲🍄⛰]+[a-zА-Я]?.+',full_msg)
        if state:
            state = state[0].split(':')[-1][1:] #geting splited : and send withoun \n
            results['status'] = state
        else:
            results['status'] = "hz"
        #TODO get gold count
        await client.disconnect()
        return results

    # Chw Functions
    async def drink_poison(self,client, p_name):
        for i in self.quest_poisons[p_name]:
            for x in i:
                await client.send_message("ChatWarsBot", (i[x])) # /use_p0*
                logger.debug(f"Trying to drink poison {i[x]}")
                await asyncio.sleep(1)

    async def mainQuestRun(self, player_obj, button):
        client = await self.client_init(player_obj.session)
        logger.debug(f"[+] {player_obj.chw_username} started!")
        stam = await self.hero_stamina(client)
        logger.debug(f"{player_obj.chw_username} {stam=}")
        if button == 3:
            stam = stam//2
            logger.debug(f"Cow button detected -> devined stamina = {stam}")
        lvl = await self.hero_level(client) #if lvl < 20: btn=0
        cast_range = AsyncIterator(range(stam))

        await self.drink_poison(client, "Nature")
        await self.drink_poison(client, "Greed")

        async for i in cast_range:
            await self.quest_auto(cli=client, lvl=lvl, button=button)

        await asyncio.sleep(3)
        await client.disconnect()
        logger.debug(f"[-] {player_obj.chw_username} disconnected")

    async def quest_auto(self, cli, lvl, button):
        """ Function that go client to quiest while have stamina """
        info = await cli(GetFullUserRequest('me'))
        #logger.debug(f"{info.user.username=} -> {cli=} -> {lvl=} -> {button=}")
        await cli.send_message("ChatWarsBot", self.quests)
        await asyncio.sleep(1)
        msg1 = await cli.get_messages("ChatWarsBot")

        if await msg1[0].click(button) == None:
            logger.error("Click failed")
            await self.quest_auto(cli, lvl, button)
        else:
            await asyncio.sleep(1)
            msg_time = await cli.get_messages("ChatWarsBot")
                #logger.debug("Message:"+msg_time[0].message)
            msg_time = re.findall("\d+", str(msg_time[0].text))
            try:
                msg_time = str(msg_time[0])
                msg_time = int(msg_time)
                msg_time *= 60
                logger.info(f"{info.user.username} time in quest: {msg_time}")
                msg_time += 10
                if button==3:
                    msg_time += 190
                await asyncio.sleep(msg_time)
                return True
            except Exception as e:
                #Битва близко. Сейчас не до приключений.
                #Ты сейчас занят другим приключением. Попробуй позже.
                logger.error(f"Something gone wrong!\n {e}")
                return False
            #await cli.send_message("ChatWarsBot", defence)
            #return None?
            #await asyncio.sleep(3)
        return False

    # sub funcs TODO Class with init and rename of cli or something else
    async def get_game_time(self, player_obj):
        """ Check and game time"""
        if (type(player_obj) == CW_players):
            client = await self.client_init(player_obj.session)
        else:
            client = player_obj
            logger.debug(f"Client was inited! His type is: {str(type(client))}!")
        msg = await self.chw_get_msg(client, self.castle)
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

    async def hero_level(self, cli):
        msg = await self.chw_get_msg(cli,self.hero)
        msg = str(msg[0].message)
        rd = re.findall("Уровень: \d+", msg)
        rs = int(re.findall("\d+",rd[0])[0])
        logger.debug("LVL "+str(rs))
        return rs

    async def hero_stamina(self, client):
        """ Check how many stamina client have  """
        #client = await client_init(sessionFromRequest)
        msg = await self.chw_get_msg(client,self.hero)
        msg = str(msg[0].message)
        stamina = re.findall("Выносливость: \d+\/\d+", msg)
        stamina = re.findall("\d+", stamina[0])
        stamina = int(stamina[0])
        return stamina


class TelethonAuth():
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
