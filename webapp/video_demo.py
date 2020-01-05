import eventlet
eventlet.monkey_patch()
from eventlet import wsgi
from flask import Flask, request, abort, render_template, jsonify, Response
from flask_socketio import SocketIO, emit
import video_opencv
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

P_left_count = 0
P_right_count = 0

@app.route("/")
def home():
    return render_template('index.html', async_mode=socketio.async_mode)

def gen(camera):
    """Video streaming generator function."""
    while True:
        vid_frame = camera.get_frame()
        left,right = camera.get_person_count()
        global P_left_count
        P_left_count = left
        global P_right_count
        P_right_count = right
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + vid_frame + b'\r\n')

@app.route("/demo_feed")
def demo_feed():
    demo_cam = video_opencv.Camera()
    return Response(gen(demo_cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

CONTROL_PIN = 17
PWM_FREQ = 50
GPIO.setmode(GPIO.BCM)
GPIO.setup(CONTROL_PIN, GPIO.OUT)
pwm = GPIO.PWM(CONTROL_PIN, PWM_FREQ)
pwm.start(0)


def angle_to_duty_cycle(angle=0):
   duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * int(angle) / 180)
   return duty_cycle

@app.route("/direction/<angle>")
def action(angle):
   pwm.ChangeDutyCycle(angle_to_duty_cycle(int(angle)))
   return '',204

@app.route("/direction/reset")
def reset(angle):
   pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
   return '',204

@app.route("/auto", methods=['POST'])
def auto():
   if P_left_count > P_right_count:
     pwm.ChangeDutyCycle(angle_to_duty_cycle(135))
   elif P_left_count < P_right_count:
     pwm.ChangeDutyCycle(angle_to_duty_cycle(45))
   else:
     pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
   return '',204

@app.route("/stop")
def stop():
   pwm.ChangeDutyCycle(angle_to_duty_cycle(90))

   return '',204

if __name__ == "__main__":
    wsgi.server(eventlet.listen(('0.0.0.0',5000)),app)
    #socketio.run(app,host='0.0.0.0', debug=True)

