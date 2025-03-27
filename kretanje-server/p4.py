import RPi.GPIO as GPIO
from time import sleep

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
pins = [11, 12,  13, 15, 16, 18, 22, 29, 31]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

pwm = GPIO.PWM(ENABCD, 30) # 30 Hz
pwm.start(0)  # Početna brzina 0%

def move_motor(IN1, IN2, direction, dutyCicle):
    pwm.ChangeDutyCycle(dutyCicle)
    GPIO.output(IN1, GPIO.HIGH if direction == "forward" else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if direction == "forward" else GPIO.HIGH)

# Primer: Pokreni motore napred 10
move_motor(motorA_IN1, motorA_IN2, "forward", 10)
move_motor(motorB_IN3, motorB_IN4, "forward", 10)
move_motor(motorC_IN1, motorC_IN2, "forward", 10)
move_motor(motorD_IN3, motorD_IN4, "forward", 10)
sleep(2)

# Primer: Pokreni motore napred 20
#move_motor(motorA_IN1, motorA_IN2, "forward", 20)
#move_motor(motorB_IN3, motorB_IN4, "forward", 20)
#move_motor(motorC_IN1, motorC_IN2, "forward", 20)
#move_motor(motorD_IN3, motorD_IN4, "forward", 20)
#sleep(2)

# Primer: Pokreni motore nazad 10
#move_motor(motorA_IN1, motorA_IN2, "backward", 10)
#move_motor(motorB_IN3, motorB_IN4, "backward", 10)
#move_motor(motorC_IN1, motorC_IN2, "backward", 10)
#move_motor(motorD_IN3, motorD_IN4, "backward", 10)
#sleep(2)

# Primer: Pokreni motore nazad 20
#move_motor(motorA_IN1, motorA_IN2, "backward", 20)
#move_motor(motorB_IN3, motorB_IN4, "backward", 20)
#move_motor(motorC_IN1, motorC_IN2, "backward", 20)
#move_motor(motorD_IN3, motorD_IN4, "backward", 20)
#sleep(2)

pwm.stop()
GPIO.cleanup()  # Očisti pinove na kraju
