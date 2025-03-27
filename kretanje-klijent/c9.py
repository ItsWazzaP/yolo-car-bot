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
    uri = "ws://192.168.8.111:1606"  # IP adresa RPi4
    
    async with websockets.connect(
        uri,
        ping_interval=20,
        ping_timeout=10
    ) as websocket:
        print("Povezan na robot. Kontrole: W/A/S/D/X (stop), Q za izlaz")
        while True:
            try:
                # Čekamo korisnički unos
                user_input = (await ainput("Komanda: ")).lower()
                
                if user_input == 'q':
                    await websocket.send("stop")
                    print("Zaustavljanje i izlaz...")
                    break
                    
                if user_input in direction_map:
                    command = direction_map[user_input]
                    await websocket.send(command)
                    print(f"Poslato: {command}")
                else:
                    print("Nevažeća komanda! Koristite W/A/S/D/X ili Q za izlaz")
                    
            except Exception as e:
                print(f"Greška: {e}")
                break

if __name__ == "__main__":
    try:
        asyncio.run(send_directions())
    except KeyboardInterrupt:
        print("\nProgram ručno zaustavljen")
    except Exception as e:
        print(f"Došlo je do greške: {e}")
