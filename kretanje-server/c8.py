# client_controller.py
import asyncio
import websockets
from aioconsole import ainput

direction_map = {
    'w': 'gore',
    's': 'dole',
    'a': 'levo',
    'd': 'desno',
    'x': 'stop'
}

async def send_directions():
    uri = "ws://localhost:1606"  # IP adresa RPi4
    
    async with websockets.connect(
        uri,
        ping_interval=20,
        ping_timeout=10
    ) as websocket:
        print("Povezan na robot. Kontrole: W/A/S/D/X (stop)")
        while True:
            try:
                user_input = await ainput("Komanda: ").lower()
                
                if user_input == 'q':
                    await websocket.send("stop")
                    break
                    
                if user_input in direction_map:
                    command = direction_map[user_input]
                    await websocket.send(command)
                    print(f"Poslato: {command}")
                else:
                    print("Nevažeća komanda!")
                    
            except Exception as e:
                print(f"Greška: {e}")
                break

asyncio.get_event_loop().run_until_complete(send_directions())
