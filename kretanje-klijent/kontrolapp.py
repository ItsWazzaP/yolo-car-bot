import tkinter as tk
from tkinter import ttk
import websockets
import asyncio
import json
from threading import Thread
from PIL import Image, ImageTk
import io
import requests

class RobotControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrola Vozila")
        self.uri = "ws://192.168.8.111:1606"
        self.camera_url = "http://192.168.8.111:1606/capture"  # Dodaj endpoint na serveru za sliku
        self.active_keys = set()
        self.ws = None
        
        # WebSocket Thread
        self.ws_thread = Thread(target=self.run_websocket, daemon=True)
        self.ws_thread.start()
        
        # GUI Setup
        self.create_controls()
        self.setup_key_bindings()
        
    def run_websocket(self):
        asyncio.run(self.websocket_client())

    async def websocket_client(self):
        async with websockets.connect(self.uri) as websocket:
            self.ws = websocket
            while True:
                await asyncio.sleep(0.1)  # Održavamo konekciju

    def create_controls(self):
        # Frame za kontrolu
        control_frame = ttk.Frame(self.root, padding=20)
        control_frame.grid(row=0, column=0)
        
        # Dugmići
        self.btn_up = ttk.Button(control_frame, text="⬆ Gore", command=lambda: self.send_command('gore', True))
        self.btn_down = ttk.Button(control_frame, text="⬇ Dole", command=lambda: self.send_command('dole', True))
        self.btn_left = ttk.Button(control_frame, text="⬅ Levo", command=lambda: self.send_command('levo', True))
        self.btn_right = ttk.Button(control_frame, text="➡ Desno", command=lambda: self.send_command('desno', True))
        
        # Postavi u grid
        self.btn_up.grid(row=0, column=1)
        self.btn_left.grid(row=1, column=0)
        self.btn_right.grid(row=1, column=2)
        self.btn_down.grid(row=2, column=1)
        
        # Dugme za sliku
        self.btn_capture = ttk.Button(control_frame, text="Snimi Sliku", command=self.capture_image)
        self.btn_capture.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Prikaz slike
        self.image_label = ttk.Label(control_frame)
        self.image_label.grid(row=4, column=0, columnspan=3)

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
            response = requests.get(self.camera_url)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
        except Exception as e:
            print(f"Greška pri snimanju: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlApp(root)
    root.mainloop()
