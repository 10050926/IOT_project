import RPi.GPIO as GPIO
import time

CONTROL_PIN = 17
PWM_FREQ = 50
STEP=15

GPIO.setmode(GPIO.BCM)
GPIO.setup(CONTROL_PIN, GPIO.OUT)
 
pwm = GPIO.PWM(CONTROL_PIN, PWM_FREQ)
pwm.start(0)

def angle_to_duty_cycle(angle=0):
    duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * angle / 180)
    return duty_cycle

try:
    print('按下 Ctrl-C 可停止程式')
    while True:
       Ki = input('key input')
       if Ki == 'd':
          pwm.ChangeDutyCycle(angle_to_duty_cycle(45))
       elif Ki == 'a':
          pwm.ChangeDutyCycle(angle_to_duty_cycle(135))
       else:
          break
    pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
    while True:
        next
except KeyboardInterrupt:
    print('關閉程式')
finally:
    pwm.stop()
    GPIO.cleanup()
