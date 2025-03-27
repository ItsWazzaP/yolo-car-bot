import asyncio
import websockets
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

async def handle_client(websocket, path):
    client_ip = websocket.remote_address[0]
    log(f"Novi klijent spojen: {client_ip}")
    try:
        async for message in websocket:
            # Proveri da li je poruka prazna
            if not message:
                log(f"Primljena prazna poruka od {client_ip}")
                continue

            # Proveri da li je poruka kontrolna
            if message in ["ping", "pong", "close"]:
                log(f"Primljena kontrolna poruka: {message} ({client_ip})")
                continue

            # Proveri da li je poruka validna komanda
            if message in ["gore", "dole", "levo", "desno"]:
                log(f"Primljen signal: {message} ({client_ip})")
            else:
                log(f"Nevažeća komanda: {message} ({client_ip})")
                await websocket.send("Nevažeća komanda!")
    except websockets.exceptions.ConnectionClosed:
        log(f"Klijent diskonektovan: {client_ip}")
    except Exception as e:
        log(f"Greška: {e}")

async def main():
    # Podešavanje servera
    start_server = await websockets.serve(
        handle_client,
        "0.0.0.0",  # IP adresa
        1606             # Port
    )
    log("Server pokrenut na ws://192.168.0.15:1606")
    await start_server.wait_closed()  # Čekaj dok server radi

# Pokretanje servera
if __name__ == "__main__":
    asyncio.run(main())
