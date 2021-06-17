import asyncio
import websockets
import requests
import time
import json

information = {"1m": {}, "5m": {}, "15m": {}, "30m": {}}

bookTicker = requests.get('https://api.binance.com/api/v3/ticker/bookTicker').json()
with open("pairs.json", 'w') as f:
    f.write("{}")
pairs = [i["symbol"] for i in bookTicker]

pairs1 = pairs[0:int(len(pairs) / 2)]
pairs2 = pairs[int(len(pairs) / 2):]
timeStart = time.time()

async def candle_stick_data(pairs, timeType):
    url = "wss://stream.binance.com:9443/ws/"  # steam address
    # first_pair = f'bnbbtc@kline_1m'  # first pair
    minute  = "@kline_" + timeType
    allPairs = '/'.join([f"{i.lower() + minute}" for i in pairs])
    async with websockets.connect(url + allPairs) as sock:
        while 1:
            resp = await sock.recv()
            resp = json.loads(resp)
            try:
                resp = resp["k"]
                inf = resp
                information[resp["i"]][resp["s"]] = inf
                # print(f"{resp}")
            except KeyError:
                continue
            if (time.time() - timeStart) > 86400:
                await sock.send(pairs)

async def writeToFile():
    print("aaa")
    while 1:
        # await asyncio.sleep(5)
        print("Запись в файл")
        try:
            with open("pairs.json", 'w') as f:
                json.dump(information, f)
        except PermissionError:
            pass

mainLoop = asyncio.get_event_loop()
tasks = [mainLoop.create_task(candle_stick_data(pairs1, "1m")), mainLoop.create_task(writeToFile()) ]
mainLoop.run_until_complete(asyncio.wait(tasks))
