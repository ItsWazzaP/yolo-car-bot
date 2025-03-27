import tkinter as tk
from tkinter import ttk
import websockets
import asyncio
from threading import Thread
from PIL import Image, ImageTk, ImageOps
import io
import requests

class RobotControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrola Vozila")
        
        # Postavke za WebSocket i kameru
        self.ws_uri = tk.StringVar(value="ws://192.168.8.111:1606")
        self.image_url = tk.StringVar(value="http://192.168.8.111:1606/capture")
        self.active_commands = set()
        self.ws = None
        self.image_label = None
        self.ws_loop = None  # Dodato za event loop management

        # Mapiranje tastera na komande
        self.key_to_command = {
            'up': 'gore',
            'down': 'dole',
            'left': 'levo',
            'right': 'desno'
        }

        # Inicijalizacija GUI
        self.create_controls()
        self.setup_key_bindings()
        
        # Pokretanje WebSocket veze
        self.ws_thread = Thread(target=self.run_websocket, daemon=True)
        self.ws_thread.start()
        
        # Početna slika
        self.show_placeholder_image()

    def create_controls(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # WebSocket URL
        ttk.Label(main_frame, text="Web socket:").grid(row=0, column=0, sticky=tk.W)
        ws_entry = ttk.Entry(main_frame, textvariable=self.ws_uri, width=40)
        ws_entry.grid(row=0, column=1, columnspan=2, pady=5, sticky=tk.EW)

        # URL za sliku
        ttk.Label(main_frame, text="Slika:").grid(row=1, column=0, sticky=tk.W)
        image_entry = ttk.Entry(main_frame, textvariable=self.image_url, width=40)
        image_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky=tk.EW)

        # Kontrolni panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.btn_up = ttk.Button(control_frame, text="⬆ Gore", command=lambda: self.send_command('gore', True))
        self.btn_down = ttk.Button(control_frame, text="⬇ Dole", command=lambda: self.send_command('dole', True))
        self.btn_left = ttk.Button(control_frame, text="⬅ Levo", command=lambda: self.send_command('levo', True))
        self.btn_right = ttk.Button(control_frame, text="➡ Desno", command=lambda: self.send_command('desno', True))
        
        self.btn_up.grid(row=0, column=1)
        self.btn_left.grid(row=1, column=0)
        self.btn_right.grid(row=1, column=2)
        self.btn_down.grid(row=2, column=1)

        # Dugme za osvežavanje slike
        self.btn_capture = ttk.Button(main_frame, text="Osveži sliku", command=self.capture_image)
        self.btn_capture.grid(row=3, column=0, columnspan=3, pady=10)

        # Prikaz slike
        self.image_label = ttk.Label(main_frame)
        self.image_label.grid(row=4, column=0, columnspan=3)

    def show_placeholder_image(self):
        placeholder = Image.new('RGB', (640, 320), color='black')
        self.tk_image = ImageTk.PhotoImage(placeholder)
        self.image_label.config(image=self.tk_image)

    def setup_key_bindings(self):
        self.root.bind('<KeyPress>', self.key_press)
        self.root.bind('<KeyRelease>', self.key_release)

    def key_press(self, event):
        key = event.keysym.lower()
        cmd = self.key_to_command.get(key)
        if cmd and cmd not in self.active_commands:
            self.active_commands.add(cmd)
            self.send_combined_command()

    def key_release(self, event):
        key = event.keysym.lower()
        cmd = self.key_to_command.get(key)
        if cmd and cmd in self.active_commands:
            self.active_commands.remove(cmd)
            self.send_combined_command()

    def send_combined_command(self):
        if not self.active_commands:
            self.send_command('stop', False)
            return
            
        if len(self.active_commands) == 1:
            command = next(iter(self.active_commands))
            self.send_command(command, False)
        else:
            self.send_command('stop', False)

    def send_command(self, cmd, is_button):
        if is_button:
            self.active_commands.clear()
            if cmd != 'stop':
                self.active_commands.add(cmd)
        
        async def async_send():
            try:
                if self.ws and not self.ws.closed:
                    await self.ws.send(cmd)
                    print(f"Uspešno poslato: {cmd}")
            except Exception as e:
                print(f"Greška pri slanju: {e}")
        
        if self.ws_loop and self.ws_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                async_send(),
                self.ws_loop
            )

    def capture_image(self):
        try:
            response = requests.get(self.image_url.get(), timeout=3)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image = ImageOps.fit(image, (640, 320), Image.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(image)
                self.image_label.config(image=self.tk_image)
        except Exception as e:
            print(f"Greška pri preuzimanju slike: {e}")

    def run_websocket(self):
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        self.ws_loop.run_until_complete(self.websocket_client())

    async def websocket_client(self):
        while True:
            try:
                async with websockets.connect(self.ws_uri.get()) as websocket:
                    self.ws = websocket
                    print("WebSocket konekcija uspostavljena")
                    
                    # Glavna petlja za održavanje konekcije
                    while True:
                        await asyncio.sleep(1)
                        if websocket.closed:
                            break
                            
            except Exception as e:
                print(f"Greška: {e}. Pokušavam ponovo za 3 sekunde...")
                await asyncio.sleep(3)
                
            finally:
                self.ws = None

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlApp(root)
    root.mainloop()