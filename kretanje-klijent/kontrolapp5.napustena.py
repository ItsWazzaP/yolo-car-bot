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
        self.root.title("Kontrola Robota")
        
        # Konfiguracija
        self.ws_uri = tk.StringVar(value="ws://192.168.8.111:1606")
        self.image_url = tk.StringVar(value="http://192.168.8.111:1606/capture")
        self.active_commands = set()
        self.ws = None
        self.image_label = None
        self.ws_loop = None
        self.auto_stop_task = None

        # Mapiranje komandi
        self.key_mapping = {
            'up': 'gore',
            'down': 'dole',
            'left': 'levo',
            'right': 'desno',
            'space': 'stop'
        }

        # GUI Inicijalizacija
        self.init_gui()
        self.setup_bindings()
        
        # Pokretanje WebSocket threada
        self.start_websocket()
        
        # Inicijalna slika
        self.show_placeholder()

    def init_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Kontrolni panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Dugmadi za kontrolu
        self.btn_up = ttk.Button(control_frame, text="⬆ GORE", command=lambda: self.send_move('gore'))
        self.btn_left = ttk.Button(control_frame, text="⬅ LEVO", command=lambda: self.send_move('levo'))
        self.btn_stop = ttk.Button(control_frame, text="⏹ STOP", command=self.send_stop)
        self.btn_right = ttk.Button(control_frame, text="➡ DESNO", command=lambda: self.send_move('desno'))
        self.btn_down = ttk.Button(control_frame, text="⬇ DOLE", command=lambda: self.send_move('dole'))
        
        # Raspored dugmadi
        self.btn_up.grid(row=0, column=1, padx=5, pady=2)
        self.btn_left.grid(row=1, column=0, padx=5, pady=2)
        self.btn_stop.grid(row=1, column=1, padx=5, pady=2)
        self.btn_right.grid(row=1, column=2, padx=5, pady=2)
        self.btn_down.grid(row=2, column=1, padx=5, pady=2)

        # Statusna traka
        self.status = ttk.Label(main_frame, text="Status: Nije spojeno", foreground="red")
        self.status.grid(row=1, column=0, columnspan=3, pady=5)

        # Kamera panel
        self.image_label = ttk.Label(main_frame)
        self.image_label.grid(row=2, column=0, columnspan=3)
        ttk.Button(main_frame, text="Osveži Kameru", command=self.capture_image).grid(row=3, column=0, columnspan=3, pady=10)

    def setup_bindings(self):
        self.root.bind('<KeyPress>', self.handle_key_press)
        self.root.bind('<KeyRelease>', self.handle_key_release)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def handle_key_press(self, event):
        cmd = self.key_mapping.get(event.keysym.lower())
        if cmd and cmd != 'stop':
            self.active_commands.add(cmd)
            self.send_combined()

    def handle_key_release(self, event):
        cmd = self.key_mapping.get(event.keysym.lower())
        if cmd in self.active_commands:
            self.active_commands.remove(cmd)
            self.send_combined()
        elif cmd == 'stop':
            self.send_stop()

    def send_combined(self):
        if not self.active_commands:
            self.send_stop()
        elif len(self.active_commands) == 1:
            self.send_move(next(iter(self.active_commands)))
        else:
            self.send_stop()

    def send_move(self, command):
        self.cancel_auto_stop()
        self.send(command)
        self.auto_stop_task = self.root.after(300, self.send_stop)

    def send_stop(self):
        self.cancel_auto_stop()
        self.send('stop')

    def cancel_auto_stop(self):
        if self.auto_stop_task:
            self.root.after_cancel(self.auto_stop_task)
            self.auto_stop_task = None

    def send(self, command):
        async def async_send():
            try:
                if self.ws and not self.ws.closed:
                    await self.ws.send(command)
                    print(f"Poslato: {command}")
                    self.status.config(text=f"Status: Aktivno - {command.upper()}", foreground="green")
            except Exception as e:
                self.status.config(text=f"Greška: {str(e)}", foreground="red")
                print(f"Greška pri slanju: {e}")

        if self.ws_loop and self.ws_loop.is_running():
            asyncio.run_coroutine_threadsafe(async_send(), self.ws_loop)

    def capture_image(self):
        try:
            response = requests.get(self.image_url.get(), timeout=3)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                img = ImageOps.fit(img, (640, 360), Image.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.tk_image)
        except Exception as e:
            print(f"Greška kamere: {e}")

    def start_websocket(self):
        def run_loop():
            self.ws_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.ws_loop)
            self.ws_loop.run_until_complete(self.websocket_task())

        self.ws_thread = Thread(target=run_loop, daemon=True)
        self.ws_thread.start()

    async def websocket_task(self):
        while True:
            try:
                async with websockets.connect(self.ws_uri.get()) as ws:
                    self.ws = ws
                    self.status.config(text="Status: Spojeno", foreground="green")
                    print("WebSocket konekcija uspostavljena")
                    
                    while True:
                        await asyncio.sleep(1)
                        if ws.closed:
                            break
                            
            except Exception as e:
                self.status.config(text="Status: Ponovno povezivanje...", foreground="orange")