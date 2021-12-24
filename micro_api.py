import aiohttp, asyncio, json, aioschedule
from loguru import logger as log

log.add("autorun_logs.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

class SheduledQuestAPI():
    async def go_quest(self, player_id, place):
        log.info(f"{player_id} started quest {place}")
        url = f"http://10.64.47.2:8080/main/player/{player_id}/"
        h = {"Accept": "application/json"}
        j = {"status": "Run", "quest": place}
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=h, json=j) as resp:
                r = await resp.text()

    async def scheduler(self):
        aioschedule.every().day.at("06:00").do(self.go_quest, 12,"forest")
        aioschedule.every().day.at("06:00").do(self.go_quest, 13,"swamp")
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

async def main():
    sqa = SheduledQuestAPI()
    print("Started handler!")
    await asyncio.create_task(sqa.scheduler())


if __name__ == "__main__":
    asyncio.run(main())
