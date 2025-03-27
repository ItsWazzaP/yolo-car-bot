import RPi.GPIO as GPIO
from time import sleep
import asyncio
import websockets
from aioconsole import ainput  # Asinhroni input

# Postavi BOARD notaciju (fizički pinovi)
GPIO.setmode(GPIO.BOARD)
ENABCD = 12    # PWM pin za brzinu

# Definiraj pinove za Module 1 i 2 (BOARD pinovi)
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

pwm = GPIO.PWM(ENABCD, 30)  # 30 Hz
pwm.start(0)  # Početna brzina 0%

def move_motor(IN1, IN2, direction, duty_cycle):
    pwm.ChangeDutyCycle(duty_cycle)
    GPIO.output(IN1, GPIO.HIGH if direction == "forward" else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if direction == "forward" else GPIO.HIGH)

def stop_motors():
    pwm.ChangeDutyCycle(0)  # Zaustavi motore
    GPIO.output(motorA_IN1, GPIO.LOW)
    GPIO.output(motorA_IN2, GPIO.LOW)
    GPIO.output(motorB_IN3, GPIO.LOW)
    GPIO.output(motorB_IN4, GPIO.LOW)
    GPIO.output(motorC_IN1, GPIO.LOW)
    GPIO.output(motorC_IN2, GPIO.LOW)
    GPIO.output(motorD_IN3, GPIO.LOW)
    GPIO.output(motorD_IN4, GPIO.LOW)

async def send_directions():
    uri = "ws://localhost:1606"  # WebSocket server adresa
    async with websockets.connect(
        uri,
        ping_interval=20,
        ping_timeout=10
    ) as websocket:
        print("Povezan na server. Koristi W/A/S/D za slanje komandi.")
        while True:
            try:
                # Asinhrono čitanje unosa
                user_input = await ainput("Unesi komandu (W/A/S/D ili Q za izlaz): ")
                user_input = user_input.lower()
                
                if user_input == 'q':
                    print("Izlazim iz programa...")
                    stop_motors()  # Zaustavi motore pre izlaza
                    break
                    
                # Slanje komandi serveru
                if user_input in ["w", "a", "s", "d"]:
                    command = {
                        "w": "gore",
                        "s": "dole",
                        "a": "levo",
                        "d": "desno"
                    }[user_input]
                    await websocket.send(command)
                    print(f"Poslato: {command}")

                    # Pokretanje motora u zavisnosti od komande
                    if command == "gore":
                        move_motor(motorA_IN1, motorA_IN2, "forward", 10)
                        move_motor(motorB_IN3, motorB_IN4, "forward", 10)
                        move_motor(motorC_IN1, motorC_IN2, "forward", 10)
                        move_motor(motorD_IN3, motorD_IN4, "forward", 10)
                    elif command == "dole":
                        move_motor(motorA_IN1, motorA_IN2, "backward", 10)
                        move_motor(motorB_IN3, motorB_IN4, "backward", 10)
                        move_motor(motorC_IN1, motorC_IN2, "backward", 10)
                        move_motor(motorD_IN3, motorD_IN4, "backward", 10)
                    elif command == "levo":
                        # Primer: Okretanje ulevo (možeš prilagoditi)
                        move_motor(motorA_IN1, motorA_IN2, "forward", 10)
                        move_motor(motorB_IN3, motorB_IN4, "backward", 10)
                        move_motor(motorC_IN1, motorC_IN2, "forward", 10)
                        move_motor(motorD_IN3, motorD_IN4, "backward", 10)
                    elif command == "desno":
                        # Primer: Okretanje udesno (možeš prilagoditi)
                        move_motor(motorA_IN1, motorA_IN2, "backward", 10)
                        move_motor(motorB_IN3, motorB_IN4, "forward", 10)
                        move_motor(motorC_IN1, motorC_IN2, "backward", 10)
                        move_motor(motorD_IN3, motorD_IN4, "forward", 10)
                else:
                    print("Nevažeća komanda! Koristi W/A/S/D")
                    
            except Exception as e:
                print(f"Greška: {e}")
                stop_motors()  # Zaustavi motore u slučaju greške
                break

# Pokretanje klijenta
print("Pokrećem klijenta...")
try:
    asyncio.get_event_loop().run_until_complete(send_directions())
finally:
    pwm.stop()
    GPIO.cleanup()  # Očisti pinove na kraju
