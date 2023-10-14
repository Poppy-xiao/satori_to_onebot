import websocket

import asyncio
import json 
import asyncio
import websockets

async def satori_communication():
    uri = "ws://127.0.0.1:5501/v1/events"
    async with websockets.connect(uri) as websocket:
        # Authentication and session recovery
        identify_signal = {
            "op": 3,
            "body": {"token": "49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136", "sequence": 0}
        }
        await websocket.send(json.dumps(identify_signal))
        # Heartbeat
        while True:
            await asyncio.sleep(10)
            ping_signal = {"op": 1}
            await websocket.send(json.dumps(ping_signal))
            # Receiving events
            event_signal = await websocket.recv()
            print(event_signal)

asyncio.run(satori_communication())
