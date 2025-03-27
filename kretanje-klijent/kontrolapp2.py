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
        
        # Default vrednosti
        self.ws_uri = tk.StringVar(value="ws://192.168.8.111:1606")
        self.image_url = tk.StringVar(value="http://192.168.8.111:1606/capture")
        
        # WebSocket i kamera
        self.active_keys = set()
        self.ws = None
        self.image_label = None
        
        # GUI Setup
        self.create_controls()
        self.setup_key_bindings()
        
        # Pokreni WebSocket u pozadini
        self.ws_thread = Thread(target=self.run_websocket, daemon=True)
        self.ws_thread.start()
        
        # Placeholder za sliku
        self.show_placeholder_image()

    def create_controls(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # WebSocket URL
        ttk.Label(main_frame, text="Web socket:").grid(row=0, column=0, sticky=tk.W)
        ws_entry = ttk.Entry(main_frame, textvariable=self.ws_uri, width=40)
        ws_entry.grid(row=0, column=1, columnspan=2, pady=5, sticky=tk.EW)

        # Image URL
        ttk.Label(main_frame, text="Slika:").grid(row=1, column=0, sticky=tk.W)
        image_entry = ttk.Entry(main_frame, textvariable=self.image_url, width=40)
        image_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky=tk.EW)

        # Kontrole
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

        # Dugme za sliku
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
        if key in ['up', 'down', 'left', 'right']:
            self.active_keys.add(key)
            self.send_combined_command()

    def key_release(self, event):
        key = event.keysym.lower()
        if key in ['up', 'down', 'left', 'right']:
            if key in self.active_keys:
                self.active_keys.remove(key)
            self.send_combined_command()

    def send_combined_command(self):
        if not self.active_keys:
            self.send_command('stop', False)
            return
            
        commands = {
            frozenset(['up', 'right']): 'desno_u_mestu',
            frozenset(['up', 'left']): 'levo_u_mestu',
            frozenset(['down', 'right']): 'nazad_desno',
            frozenset(['down', 'left']): 'nazad_levo',
        }
        
        current = frozenset(self.active_keys)
        command = commands.get(current, list(self.active_keys)[0] if len(self.active_keys) == 1 else 'stop')
        self.send_command(command, False)

    def send_command(self, cmd, is_button):
        if is_button:
            self.active_keys.clear()
            if cmd != 'stop':
                self.active_keys.add(cmd.split('_')[0])
                
        if self.ws and self.ws.open:
            asyncio.run_coroutine_threadsafe(self.ws.send(cmd), asyncio.get_event_loop())
            print(f"Poslato: {cmd}")

    def capture_image(self):
        try:
            response = requests.get(self.image_url.get())
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image = ImageOps.fit(image, (640, 320), Image.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(image)
                self.image_label.config(image=self.tk_image)
        except Exception as e:
            print(f"Greška pri preuzimanju slike: {e}")

    def run_websocket(self):
        asyncio.run(self.websocket_client())

    async def websocket_client(self):
        try:
            async with websockets.connect(self.ws_uri.get()) as websocket:
                self.ws = websocket
                while True:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"WebSocket greška: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlApp(root)
    root.mainloop()
