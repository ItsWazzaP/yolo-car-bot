# client.py
import asyncio
import websockets

# Mapiranje tastera na komande
direction_map = {
    'w': 'gore',
    's': 'dole',
    'a': 'levo',
    'd': 'desno'
}

# Funkcija za slanje komandi
async def send_directions():
    uri = "ws://localhost:1606"  # Nova WebSocket server adresa
    async with websockets.connect(uri) as websocket:
        print("Povezan na server. Koristi W/A/S/D za slanje komandi.")
        while True:
            try:
                # Unos komande od korisnika
                user_input = input("Unesi komandu (W/A/S/D ili Q za izlaz): ").lower()
                
                # Izlaz iz programa
                if user_input == 'q':
                    print("Izlazim iz programa...")
                    break
                
                # Slanje validne komande
                if user_input in direction_map:
                    command = direction_map[user_input]
                    await websocket.send(command)
                    print(f"Poslato: {command}")
                else:
                    print("Nevažeća komanda! Koristi W/A/S/D")
                    
            except Exception as e:
                print(f"Greška: {e}")
                break

# Pokretanje klijenta
print("Pokrećem klijenta...")
asyncio.get_event_loop().run_until_complete(send_directions())
