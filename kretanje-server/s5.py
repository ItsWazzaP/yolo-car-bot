# server.py
import asyncio
import websockets
from datetime import datetime

# Funkcija za logovanje
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# Handler za svakog klijenta
async def handle_client(websocket, path):
    client_ip = websocket.remote_address[0]
    log(f"Novi klijent spojen: {client_ip}")
    
    try:
        async for message in websocket:
            # Validacija primljenih komandi
            if message in ["gore", "dole", "levo", "desno"]:
                log(f"Primljen signal: {message} ({client_ip})")
            else:
                log(f"Nevažeća komanda: {message} ({client_ip})")
                await websocket.send("Nevažeća komanda!")
                
    except websockets.exceptions.ConnectionClosed:
        log(f"Klijent diskonektovan: {client_ip}")
    except Exception as e:
        log(f"Greška: {e}")

# Pokretanje WebSocket servera
start_server = websockets.serve(
    handle_client,  # Handler funkcija
    "0.0.0.0",  # Nova IP adresa servera
    1606            # Port
)

# Logovanje pokretanja servera
log("Server pokrenut na ws://192.168.0.15:1606")

# Pokretanje asinhronog event loop-a
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
