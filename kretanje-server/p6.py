import RPi.GPIO as GPIO
import websockets
import asyncio
from datetime import datetime
from time import sleep

# Konfiguracija GPIO
GPIO.setmode(GPIO.BOARD)
ENABCD = 12    # PWM pin za brzinu

# Definiraj pinove za motore (BOARD pinovi)
motorA_IN1 = 11
motorA_IN2 = 13
motorB_IN3 = 15
motorB_IN4 = 16
motorC_IN1 = 18
motorC_IN2 = 22
motorD_IN3 = 29
motorD_IN4 = 31

# Postavi sve pinove kao izlaze
pins = [11, 12, 13, 15, 16, 18, 22, 29, 31]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# PWM konfiguracija
pwm = GPIO.PWM(ENABCD, 30)  # 30 Hz
pwm.start(0)  # Početna brzina 0%

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def move_motor(IN1, IN2, direction, duty_cycle=10):
    pwm.ChangeDutyCycle(duty_cycle)
    GPIO.output(IN1, GPIO.HIGH if direction == "forward" else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if direction == "forward" else GPIO.HIGH)

def stop_motors():
    pwm.ChangeDutyCycle(0)
    for pin in [motorA_IN1, motorA_IN2, motorB_IN3, motorB_IN4, 
                motorC_IN1, motorC_IN2, motorD_IN3, motorD_IN4]:
        GPIO.output(pin, GPIO.LOW)

async def handle_client(websocket, path):
    client_ip = websocket.remote_address[0]
    log(f"Novi klijent spojen: {client_ip}")
    
    try:
        async for message in websocket:
            if not message:
                continue


            log(f"Primljena komanda: {message} ({client_ip})")
            
            if message == "gore":
                # Napred - svi moteri napred
                move_motor(motorA_IN1, motorA_IN2, "forward")
                move_motor(motorB_IN3, motorB_IN4, "forward")
                move_motor(motorC_IN1, motorC_IN2, "forward")
                move_motor(motorD_IN3, motorD_IN4, "forward")
                
            elif message == "dole":
                # Nazad - svi moteri nazad
                move_motor(motorA_IN1, motorA_IN2, "backward")
                move_motor(motorB_IN3, motorB_IN4, "backward")
                move_motor(motorC_IN1, motorC_IN2, "backward")
                move_motor(motorD_IN3, motorD_IN4, "backward")
                
            elif message == "levo":
                # Levo - moteri A i C napred, B i D nazad
                move_motor(motorA_IN1, motorA_IN2, "forward")
                move_motor(motorB_IN3, motorB_IN4, "backward")
                move_motor(motorC_IN1, motorC_IN2, "forward")
                move_motor(motorD_IN3, motorD_IN4, "backward")
                
            elif message == "desno":
                # Desno - moteri A i C nazad, B i D napred
                move_motor(motorA_IN1, motorA_IN2, "backward")
                move_motor(motorB_IN3, motorB_IN4, "forward")
                move_motor(motorC_IN1, motorC_IN2, "backward")
                move_motor(motorD_IN3, motorD_IN4, "forward")
                
            elif message == "stop":  
                log("Примљен сигнал за STOP")
                stop_motors()
                            
            else:
                await websocket.send("Nevažeća komanda!")
                log(f"Nevažeća komanda: {message}")

    except websockets.exceptions.ConnectionClosed:
        log(f"Klijent diskonektovan: {client_ip}")
        stop_motors()
    except Exception as e:
        log(f"Greška: {e}")
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
    log("Server pokrenut na ws://0.0.0.0:1606")
    await server.wait_closed()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    log("Server zaustavljen")
finally:
    pwm.stop()
    GPIO.cleanup()
    log("GPIO resursi oslobođeni")
