import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

IN1 = 11  # ??????? ??? 11 (GPIO17)
IN2 = 13  # ??????? ??? 13 (GPIO27)
IN3 = 15  # ??????? ??? 15 (GPIO22)
IN4 = 16  # ??????? ??? 16 (GPIO23)
IN5 = 29  # ??????? ??? 29 (GPIO5)
IN6 = 31  # ??????? ??? 31 (GPIO6)
IN7 = 33  # ??????? ??? 33 (GPIO13)
IN8 = 35  # ??????? ??? 35 (GPIO19)
ENA = 12  # ??????? ??? 12 (GPIO18)

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(IN5, GPIO.OUT)
GPIO.setup(IN6, GPIO.OUT)
GPIO.setup(IN7, GPIO.OUT)
GPIO.setup(IN8, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

GPIO.output(ENA, GPIO.HIGH)

try:
    while True:
        GPIO.output(IN7, GPIO.HIGH)
        GPIO.output(IN8, GPIO.LOW)
        print("desni zadnji jedan")
        time.sleep(2)

        GPIO.output(IN7, GPIO.LOW)
        GPIO.output(IN8, GPIO.LOW)
        print("zaustavi")
        time.sleep(1)

        GPIO.output(IN7, GPIO.LOW)
        GPIO.output(IN8, GPIO.HIGH)
        print("desni zadnji drugi smer")
        time.sleep(2)

except KeyboardInterrupt:
    GPIO.output(IN7, GPIO.LOW)
    GPIO.output(IN8, GPIO.LOW)
    GPIO.cleanup()
    print("kraj")
