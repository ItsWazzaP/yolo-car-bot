import websockets
import asyncio
from datetime import datetime
from gpiozero import PWMOutputDevice, DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

# Иницијализација фабрике са BOARD нумерацијом
factory = LGPIOFactory()

# Мапа BOARD pin -> BCM pin за RPi5 (кључно!)
mapa = {
    11: 17,   # BOARD 11 -> GPIO17
    12: 18,   # BOARD 12 -> GPIO18
    13: 27,   # BOARD 13 -> GPIO27
    15: 22,   # BOARD 15 -> GPIO22
    16: 23,   # BOARD 16 -> GPIO23
    18: 24,   # BOARD 18 -> GPIO24
    22: 25,   # BOARD 22 -> GPIO25
    29: 5,    # BOARD 29 -> GPIO5
    31: 6     # BOARD 31 -> GPIO6
}

# Конфигурација GPIO са пресликавањем
ENABCD = PWMOutputDevice(pin=mapa[12], frequency=50, pin_factory=factory)

# Дефиниши пинове за моторе (BOARD нотација кроз мапу)
motorA_IN1 = DigitalOutputDevice(pin=mapa[11], pin_factory=factory)
motorA_IN2 = DigitalOutputDevice(pin=mapa[13], pin_factory=factory)
motorB_IN3 = DigitalOutputDevice(pin=mapa[15], pin_factory=factory)
motorB_IN4 = DigitalOutputDevice(pin=mapa[16], pin_factory=factory)
motorC_IN1 = DigitalOutputDevice(pin=mapa[18], pin_factory=factory)
motorC_IN2 = DigitalOutputDevice(pin=mapa[22], pin_factory=factory)
motorD_IN3 = DigitalOutputDevice(pin=mapa[29], pin_factory=factory)
motorD_IN4 = DigitalOutputDevice(pin=mapa[31], pin_factory=factory)

# Листа свих мотор пинова (остаје иста)
motor_pins = [motorA_IN1, motorA_IN2, 
              motorB_IN3, motorB_IN4,
              motorC_IN1, motorC_IN2,
              motorD_IN3, motorD_IN4]

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def move_motor(in1, in2, direction, duty_cycle=0.3):
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
            
            if message == "napred":
                move_motor(motorA_IN1, motorA_IN2, "forward")
                move_motor(motorB_IN3, motorB_IN4, "forward")
                move_motor(motorC_IN1, motorC_IN2, "forward")
                move_motor(motorD_IN3, motorD_IN4, "forward")
                
            elif message == "nazad":
                move_motor(motorA_IN1, motorA_IN2, "backward")
                move_motor(motorB_IN3, motorB_IN4, "backward")
                move_motor(motorC_IN1, motorC_IN2, "backward")
                move_motor(motorD_IN3, motorD_IN4, "backward")
                
            elif message == "levo":
                move_motor(motorA_IN1, motorA_IN2, "backward")
                move_motor(motorB_IN3, motorB_IN4, "forward")
                move_motor(motorC_IN1, motorC_IN2, "backward")
                move_motor(motorD_IN3, motorD_IN4, "forward")
                
            elif message == "desno":
                move_motor(motorA_IN1, motorA_IN2, "forward")
                move_motor(motorB_IN3, motorB_IN4, "backward")
                move_motor(motorC_IN1, motorC_IN2, "forward")
                move_motor(motorD_IN3, motorD_IN4, "backward")                
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
        # Нема потребе за pigpiod!
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Сервер заустављен")
    finally:
        ENABCD.close()
        for pin in motor_pins:
            pin.close()
        log("GPIO ресурси ослобођени")
