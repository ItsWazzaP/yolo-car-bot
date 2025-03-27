import asyncio
import websockets
from aioconsole import ainput  # Asinhroni input

direction_map = {
    'w': 'gore',
    's': 'dole',
    'a': 'levo',
    'd': 'desno'
}

async def send_directions():
    uri = "ws://localhost:1606"
    async with websockets.connect(
        uri,
        ping_interval=20,
        ping_timeout=10
    ) as websocket:
        print("Povezan na server. Koristi W/A/S/D za slanje komandi.")
        while True:
            try:
                # Asinhrono čitanje unosa
                user_input = await ainput("Unesi komandu (W/A/S/D ili Q za izlaz): ")
                user_input = user_input.lower()
                
                if user_input == 'q':
                    print("Izlazim iz programa...")
                    break
                    
                if user_input in direction_map:
                    command = direction_map[user_input]
                    await websocket.send(command)
                    print(f"Poslato: {command}")
                else:
                    print("Nevažeća komanda! Koristi W/A/S/D")
                    
            except Exception as e:
                print(f"Greška: {e}")
                break

print("Pokrećem klijenta...")
asyncio.get_event_loop().run_until_complete(send_directions())
