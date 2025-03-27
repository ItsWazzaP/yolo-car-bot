import websockets
import asyncio
from datetime import datetime
from gpiozero import PWMOutputDevice, DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from aiohttp import web
from picamera2 import Picamera2
from io import BytesIO

# Inicijalizacija kamere
camera = Picamera2()
camera.resolution = (640, 480)

# GPIO konfiguracija
factory = LGPIOFactory()
mapa = {
    11: 17, 12: 18, 13: 27, 15: 22,
    16: 23, 18: 24, 22: 25, 29: 5, 31: 6
}

ENABCD = PWMOutputDevice(pin=mapa[12], frequency=50, pin_factory=factory)

# Definicija pinova za motore
motorA_IN1 = DigitalOutputDevice(pin=mapa[11], pin_factory=factory)
motorA_IN2 = DigitalOutputDevice(pin=mapa[13], pin_factory=factory)
motorB_IN3 = DigitalOutputDevice(pin=mapa[15], pin_factory=factory)
motorB_IN4 = DigitalOutputDevice(pin=mapa[16], pin_factory=factory)
motorC_IN1 = DigitalOutputDevice(pin=mapa[18], pin_factory=factory)
motorC_IN2 = DigitalOutputDevice(pin=mapa[22], pin_factory=factory)
motorD_IN3 = DigitalOutputDevice(pin=mapa[29], pin_factory=factory)
motorD_IN4 = DigitalOutputDevice(pin=mapa[31], pin_factory=factory)

motor_pins = [motorA_IN1, motorA_IN2, motorB_IN3, motorB_IN4,
              motorC_IN1, motorC_IN2, motorD_IN3, motorD_IN4]

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def move_motor(in1, in2, direction, duty_cycle=0.3):
    ENABCD.value = duty_cycle
    if direction == "forward":
        in1.on()
        in2.off()
    elif direction == "backward":
        in1.off()
        in2.on()
    elif direction == "stop":
        in1.off()
        in2.off()

def stop_motors():
    ENABCD.value = 0
    for pin in motor_pins:
        pin.off()

async def websocket_handler(websocket, path):
    client_ip = websocket.remote_address[0]
    log(f"Novi klijent: {client_ip}")
    
    try:
        async for message in websocket:
            message = message.strip().lower()
            log(f"Primljena komanda: {message} ({client_ip})")
            
            parts = sorted(message.split('+'))
            
            if 'stop' in parts:
                stop_motors()
                continue
                
            if len(parts) == 1:
                cmd = parts[0]
                if cmd == "napred":
                    for m in [motorA_IN1, motorB_IN3, motorC_IN1, motorD_IN3]:
                        move_motor(m, motorA_IN2 if m == motorA_IN1 else 
                                   motorB_IN4 if m == motorB_IN3 else
                                   motorC_IN2 if m == motorC_IN1 else motorD_IN4, "forward")
                elif cmd == "nazad":
                    for m in [motorA_IN1, motorB_IN3, motorC_IN1, motorD_IN3]:
                        move_motor(m, motorA_IN2 if m == motorA_IN1 else 
                                   motorB_IN4 if m == motorB_IN3 else
                                   motorC_IN2 if m == motorC_IN1 else motorD_IN4, "backward")
                elif cmd == "levo":
                    move_motor(motorA_IN1, motorA_IN2, "backward")
                    move_motor(motorB_IN3, motorB_IN4, "forward")
                    move_motor(motorC_IN1, motorC_IN2, "backward")
                    move_motor(motorD_IN3, motorD_IN4, "forward")
                elif cmd == "desno":
                    move_motor(motorA_IN1, motorA_IN2, "forward")
                    move_motor(motorB_IN3, motorB_IN4, "backward")
                    move_motor(motorC_IN1, motorC_IN2, "forward")
                    move_motor(motorD_IN3, motorD_IN4, "backward")
                else:
                    await websocket.send("Nepoznata komanda!")
            elif len(parts) == 2:
                left, right = parts
                if {left, right} == {"napred", "desno"}:
                    move_motor(motorA_IN1, motorA_IN2, "forward")
                    move_motor(motorB_IN3, motorB_IN4, "forward")
                    move_motor(motorC_IN1, motorC_IN2, "stop")
                    move_motor(motorD_IN3, motorD_IN4, "stop")
                elif {left, right} == {"napred", "levo"}:
                    move_motor(motorA_IN1, motorA_IN2, "stop")
                    move_motor(motorB_IN3, motorB_IN4, "stop")
                    move_motor(motorC_IN1, motorC_IN2, "forward")
                    move_motor(motorD_IN3, motorD_IN4, "forward")
                elif {left, right} == {"nazad", "desno"}:
                    move_motor(motorA_IN1, motorA_IN2, "backward")
                    move_motor(motorB_IN3, motorB_IN4, "backward")
                    move_motor(motorC_IN1, motorC_IN2, "stop")
                    move_motor(motorD_IN3, motorD_IN4, "stop")
                elif {left, right} == {"nazad", "levo"}:
                    move_motor(motorA_IN1, motorA_IN2, "stop")
                    move_motor(motorB_IN3, motorB_IN4, "stop")
                    move_motor(motorC_IN1, motorC_IN2, "backward")
                    move_motor(motorD_IN3, motorD_IN4, "backward")
                else:
                    await websocket.send("Nevalidna kombinacija!")
            else:
                await websocket.send("Previ?e komandi!")
                
    except Exception as e:
        log(f"Gre?ka: {e}")
        stop_motors()

async def capture_image(request):
    try:
        stream = BytesIO()
        camera.capture(stream, 'jpeg')
        stream.seek(0)
        return web.Response(body=stream.read(), content_type='image/jpeg')
    except Exception as e:
        log(f"Gre?ka pri snimanju: {e}")
        return web.Response(status=500)

async def main():
    # WebSocket server
    ws_server = await websockets.serve(websocket_handler, "0.0.0.0", 1606)
    
    # HTTP server
    app = web.Application()
    app.router.add_get('/capture', capture_image)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 1607).start()
    
    log("Server pokrenut na:\n- WS: ws://0.0.0.0:1606\n- HTTP: http://0.0.0.0:1607/capture")
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server zaustavljen")
    finally:
        camera.close()
        stop_motors()
        ENABCD.close()
        for pin in motor_pins:
            pin.close()
