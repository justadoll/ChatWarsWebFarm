from telethon.sync import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import AuthKeyUnregisteredError

from main.models import CW_players
from django.conf import settings
import asyncio
from emoji import emojize
import re

logger = settings.LOGGER

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
        await client.connect()
        return client

    async def chw_get_msg(self, client,mode):
        try:
            await client.send_message('ChatWarsBot', mode)
            await asyncio.sleep(1.5)
            msg = await client.get_messages("ChatWarsBot")
            return msg
        except AuthKeyUnregisteredError:
            return

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
        if not res:
            logger.error(f"{player_obj.pk}:{player_obj.chw_username} logouted!")
            return
        full_msg = res[0].message
        
        # scrapping data from hero message to update it in db
        client_data = await client.get_me()
        splited_full_msg = full_msg.split("\n")
        if "🌟Поздравляем! Новый уровень!🌟" in full_msg:
            results["lvlup"] = True
            if full_msg.startswith("❗"):
                chw_name = splited_full_msg[7]
            else:
                chw_name = splited_full_msg[5]
        else:
            if full_msg.startswith("❗"):
                chw_name = splited_full_msg[4]
            else:
                logger.debug(f"{splited_full_msg=}")
            results["lvlup"] = False

        full_chw_name = chw_name.split(" ")
        results["player_username"] = full_chw_name[0]
        results["player_class"] = full_chw_name[1]
        if len(full_chw_name) > 3:
            logger.debug(f"chw username is > 3, {full_chw_name=}")
            results["player_class"] = full_chw_name[2]
            
        results["username"] = client_data.username
        results["phone"] = client_data.phone

        rd = re.findall("Уровень: \d+", full_msg)
        lvl = int(re.findall("\d+",rd[0])[0])
        results['lvl'] = lvl

        state = re.findall('Состояние:\n[🛌🛡⚔🔎🐫📯🌲🍄⛰]+[a-zА-Я]?.+',full_msg)
        if state:
            state = state[0].split(':')[-1][1:] #geting splited : and send withoun \n
            results['status'] = state
        else:
            results['status'] = "¯\_(ツ)_/¯"
        await client.disconnect()
        logger.debug(f"{results=}")
        return results

    async def chat_shell(self,player_obj,command):
        client = await self.client_init(player_obj.session)
        message = await self.chw_get_msg(client, command)
        results = {}
        results["text"] = message[0].message
        if not message[0].reply_markup:
            results["buttons"] = ["🏅Герой","🍺Таверна","🎲Играть в кости","🏚Лавка","⚖️Биржа","▶️Быстрый бой"]
        else:
            rowlen = len(message[0].reply_markup.rows)
            try:
                buttons_array = []
                for i in range(rowlen):
                    buttons = message[0].reply_markup.rows[i].buttons
                    for b in buttons:
                        buttons_array.append(b.text)
            except Exception as e:
                logger.error(f"{e=}")
            else:
                results["buttons"] = buttons_array
        await client.disconnect()
        return results

    # Chw Functions
    async def drink_poison(self,client, p_name):
        for i in self.quest_poisons[p_name]:
            for x in i:
                await client.send_message("ChatWarsBot", (i[x])) # /use_p0*
                logger.debug(f"Trying to drink poison {i[x]}")
                await asyncio.sleep(1)

    async def torch(self, client):
        logger.debug("Crafting tch...")
        await self.chw_get_msg(client, "/c_tch")
        logger.debug("Binding...")
        await self.chw_get_msg(client, "/bind_tch")
        res = await self.chw_get_msg(client, "/on_tch")
        msg = str(res[0].message)
        logger.debug(f"{msg=}")

    async def status(self, players_list):
        results = {}
        for player in players_list:
            client = await self.client_init(player.session)
            message = await self.chw_get_msg(client=client, mode=self.hero)
            message = message[0].message
            restatus = re.findall(r"Состояние:\n.+", message)
            restamina = re.findall("Выносливость: \d+\/\d+", message)
            regold_and_pogs = re.findall("💰[-+]?\d+ 👝\d+ 💎\d+",message)
            regold_and_sapf = re.findall("💰[-+]?\d+ 💎\d+",message)
            results[player.chw_username] = {"status":self.check_result(restatus), "stamina":self.check_result(restamina), "gold_n_pogs":self.check_result(regold_and_pogs), "gold_n_sapf":self.check_result(regold_and_sapf)}
            await client.disconnect()
        return results
    
    def check_result(self, val):
        if val:
            return val[0]
    async def command(self, players_list, command):
        results = {}
        for player in players_list:
            client = await self.client_init(player.session)
            response = await self.chw_get_msg(client=client, mode=command)
            results[player.chw_username] = response[0].message
        return results

    async def atack(self, players_list, target):
        results = []
        for player in players_list:
            client = await self.client_init(player.session)
            await self.chw_get_msg(client=client, mode="⚔Атака")
            response = await self.chw_get_msg(client=client, mode=target)
            if response[0].message.startswith("Ты приготовился к атаке"):
                results.append({player.chw_username:"✅"})
            else:
                results.append({player.chw_username:"⛔️"})
            await client.disconnect()
        return results

    async def defc(self, players_list):
        results = []
        for player in players_list:
            client = await self.client_init(player.session)
            response = await self.chw_get_msg(client=client, mode="🛡Защита")
            if response[0].message.startswith("Ты приготовился к защите"):
                results.append({player.chw_username:"✅"})
            else:
                results.append({player.chw_username:"⛔️"})
            await client.disconnect()
        return results

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
        
        await self.torch(client)
        await self.drink_poison(client, "Nature")
        await self.drink_poison(client, "Greed")

        resutls_array = {"gold":"", "exp":"", "materials":{}}
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
            msg_time = re.findall("\d+", str(msg_time[0].text))
            try:
                msg_time = int(msg_time[0])
                msg_time *= 60
                logger.info(f"{info.user.username} time in quest: {msg_time}")
                msg_time += 10
                if button==3:
                    msg_time += 190
                await asyncio.sleep(msg_time)
                results_msg = await cli.get_messages("ChatWarsBot")
                logger.debug(f"{results_msg[0].text=}")
                self.count_results(message=results_msg[0].text)
                #return True
            except Exception as e:
                logger.error(f"Something gone wrong!\n {e}")
                #return False
        return
        #return False
    def count_results(self, message):
        message = message.split('\n')
        for text in message:
            if text.startswith('Получено:'):
                logger.debug(f"Erned: {text=}")
            else:
                logger.debug(f"Not erned: {text=}")

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

    async def def_cow(self, client):
        logger.debug("Connecting...")
        await client.connect()
        me = await client.get_me()
        logger.info(f"[+] {me.first_name} connected!")
        #await client.disconnect()

        @client.on(events.NewMessage(chats=("ChatWarsBot")))
        async def def_cow_handler(event):
            await asyncio.sleep(1)
            new_msg = event.message
            if new_msg.message.endswith("КОРОВАН."):
                logger.info(f"Detected a cow! Making delay...")
                await asyncio.sleep(28)
                msg = await client.get_messages("ChatWarsBot")
                if await msg[0].click(0) == None:
                    await msg[0].click()
                    logger.error("None was detected, replying click...")
                else:
                    logger.info(f"Successfully defended cow from first time!")
                    await client.disconnect()
            else:
                pass
        
        await client.run_until_disconnected()
        logger.info("[-] Client disconnected!")
