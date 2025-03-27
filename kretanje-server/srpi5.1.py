import websockets
import asyncio
from datetime import datetime
from gpiozero import PWMOutputDevice, DigitalOutputDevice
#from gpiozero.pins.pigpio import PiGPIOFactory

from gpiozero.pins.lgpio import LGPIOFactory
factory = LGPIOFactory()
# Користимо PiGPIOFactory за бољу перформансу и BOARD нумерацију
#factory = PiGPIOFactory()

# Конфигурација GPIO са gpiozero (BOARD pinovi)
ENABCD = PWMOutputDevice(pin=12, frequency=30, pin_factory=factory)  # BOARD pin 12

# Дефиниши пинове за моторе (BOARD нотација)
motorA_IN1 = DigitalOutputDevice(pin=11, pin_factory=factory)  # BOARD 11
motorA_IN2 = DigitalOutputDevice(pin=13, pin_factory=factory)  # BOARD 13
motorB_IN3 = DigitalOutputDevice(pin=15, pin_factory=factory)  # BOARD 15
motorB_IN4 = DigitalOutputDevice(pin=16, pin_factory=factory)  # BOARD 16
motorC_IN1 = DigitalOutputDevice(pin=18, pin_factory=factory)  # BOARD 18
motorC_IN2 = DigitalOutputDevice(pin=22, pin_factory=factory)  # BOARD 22
motorD_IN3 = DigitalOutputDevice(pin=29, pin_factory=factory)  # BOARD 29
motorD_IN4 = DigitalOutputDevice(pin=31, pin_factory=factory)  # BOARD 31

# Листа свих мотор пинова за лакше управљање
motor_pins = [motorA_IN1, motorA_IN2, 
              motorB_IN3, motorB_IN4,
              motorC_IN1, motorC_IN2,
              motorD_IN3, motorD_IN4]

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def move_motor(in1, in2, direction, duty_cycle=0.1):
    """Управља једним мотором"""
    ENABCD.value = duty_cycle
    if direction == "forward":
        in1.on()
        in2.off()
    else:
        in1.off()
        in2.on()

def stop_motors():
    """Зауставља све моторе"""
    ENABCD.value = 0
    for pin in motor_pins:
        pin.off()

async def handle_client(websocket, path):
    client_ip = websocket.remote_address[0]
    log(f"Нови клијент спојен: {client_ip}")
    
    try:
        async for message in websocket:
            if not message:
                continue

            log(f"Примљена команда: {message} ({client_ip})")
            
            if message == "gore":
                move_motor(motorA_IN1, motorA_IN2, "forward")
                move_motor(motorB_IN3, motorB_IN4, "forward")
                move_motor(motorC_IN1, motorC_IN2, "forward")
                move_motor(motorD_IN3, motorD_IN4, "forward")
                
            elif message == "dole":
                move_motor(motorA_IN1, motorA_IN2, "backward")
                move_motor(motorB_IN3, motorB_IN4, "backward")
                move_motor(motorC_IN1, motorC_IN2, "backward")
                move_motor(motorD_IN3, motorD_IN4, "backward")
                
            elif message == "levo":
                move_motor(motorA_IN1, motorA_IN2, "forward")
                move_motor(motorB_IN3, motorB_IN4, "backward")
                move_motor(motorC_IN1, motorC_IN2, "forward")
                move_motor(motorD_IN3, motorD_IN4, "backward")
                
            elif message == "desno":
                move_motor(motorA_IN1, motorA_IN2, "backward")
                move_motor(motorB_IN3, motorB_IN4, "forward")
                move_motor(motorC_IN1, motorC_IN2, "backward")
                move_motor(motorD_IN3, motorD_IN4, "forward")
                
            elif message == "stop":  
                log("Примљен сигнал за STOP")
                stop_motors()
                            
            else:
                await websocket.send("Неважећа команда!")
                log(f"Неважећа команда: {message}")

    except websockets.exceptions.ConnectionClosed:
        log(f"Клијент дисконектован: {client_ip}")
        stop_motors()
    except Exception as e:
        log(f"Грешка: {e}")
        stop_motors()

async def main():
    server = await websockets.serve(
        handle_client,
        "0.0.0.0",
        1606,
        reuse_port=True,  
        ping_interval=60,
        ping_timeout=30
    )
    log("Сервер покренут на ws://0.0.0.0:1606")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        # Потребно је покренути pigpiod демон
        import subprocess
        subprocess.run(["sudo", "pigpiod"])
        
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Сервер заустављен")
    finally:
        # Ослобађање GPIO ресурса
        ENABCD.close()
        for pin in motor_pins:
            pin.close()
        log("GPIO ресурси ослобођени")
