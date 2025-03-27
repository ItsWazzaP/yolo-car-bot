import RPi.GPIO as GPIO
from time import sleep

# Дефиниција пинова (BCM нумерирање)
ENA = 18  # GPIO18 (Pin 12)
IN1 = 17  # GPIO17 (Pin 11)
IN2 = 27  # GPIO27 (Pin 13)

# Подешавање режима и пинова
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Иницијализација PWM на ENA (фреквенција=1000 Hz)
pwm = GPIO.PWM(ENA, 30)
pwm.start(0)  # Почиње са 0% duty cycle

# Постави правац мотора (напред)
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

try:
    # Степен 1: 1V (30% duty cycle од 3.3V)
    pwm.ChangeDutyCycle(10)  # 3.3V * 30% ≈ 1V
    sleep(2)

    # Степен 2: 2V (60% duty cycle од 3.3V)
    pwm.ChangeDutyCycle(20)  # 3.3V * 60% ≈ 2V
    sleep(2)

finally:
    pwm.stop()
    GPIO.cleanup()
