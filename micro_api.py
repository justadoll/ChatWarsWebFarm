import aiohttp, asyncio, json, aioschedule
import datetime as dt

class SheduledQuestAPI():
    async def go_quest(self, player_id, place):
        url = f"http://127.0.0.1:8000/main/player/{player_id}/"
        print(url)
        h = {"Accept": "application/json"}
        j = {"status": "Run", "quest": place}
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=h, json=j) as resp:
                r = await resp.text()
        return json.loads(r)

    async def scheduler(self):
        aioschedule.every().day.at("00:25").do(self.go_quest, 14,"cow")
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

async def main():
    sqa = SheduledQuestAPI()
    await asyncio.create_task(sqa.scheduler())


if __name__ == "__main__":
    asyncio.run(main())
