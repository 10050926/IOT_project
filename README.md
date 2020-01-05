# IOT_project: 指引系統
透過鏡頭及物件偵測模型判斷人們的主要行徑方向或排隊多寡，並透過告示牌指引人們至人數較少的方向，分散人流。使用者可透過網頁手動或自動控制告示牌。

所需材料：  
樹莓派* 1  
鏡頭* 1   
伺服馬達sg90(可控角度)* 1  
Intel neural compute stick 2* 1  
杜邦線(公對母)* 1  
紙箱  
膠帶  

# 步驟一：安裝openVino
__注意不要使用python3.6__  
參考教學：https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html#install-package  
Go to the directory in which you downloaded the OpenVINO toolkit.  
```程式語言
cd ~/Downloads/
```
Create an installation folder
```程式語言
sudo mkdir -p /opt/intel/openvino
```
Unpack the archive:
```程式語言
sudo tar -xf  l_openvino_toolkit_runtime_raspbian_p_<version>.tgz --strip 1 -C /opt/intel/openvino
```
Set the Environment Variables
```程式語言
echo "source /opt/intel/openvino/bin/setupvars.sh" >> ~/.bashrc
```
## 測試模型
使用模型：person-detection-retail-0013  
參考網址：https://docs.openvinotoolkit.org/2018_R5/_docs_Retail_object_detection_pedestrian_rmnet_ssd_0013_caffe_desc_person_detection_retail_0013.html  
範例程式碼：personDetection.py  
參考教學：https://stackoverflow.com/questions/55345798/how-to-use-openvino-pre-trained-models  
確保模型含有下列兩檔案：  
person-detection-retail-0013.xml  
person-detection-retail-0013.bin  

透過cv2讀取模型  
```程式語言=python
model_path = "person-detection-retail-0013.xml"
pbtxt_path = "person-detection-retail-0013.bin"
net = cv2.dnn.readNet(model_path,pbtxt_path)
```
設定使用neural compute stick跑  
```程式語言=python
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
```
# 步驟二：接鏡頭及伺服馬達
樹莓派GPIO參考：https://pinout.xyz/  
伺服馬達使用、連接參考：https://blog.everlearn.tw/%E7%95%B6-python-%E9%81%87%E4%B8%8A-raspberry-pi/raspberry-pi-3-mobel-3-%E5%88%A9%E7%94%A8-pwm-%E6%8E%A7%E5%88%B6%E4%BC%BA%E6%9C%8D%E9%A6%AC%E9%81%94  
使用BCM 17 pin作為SG90 pwm控制  
範例程式碼：sg90.py  

# 步驟三：安裝flask & Socketio & eventlet
flask參考網址：https://www.palletsprojects.com/p/flask/  
安裝flask  
```程式語言=python
pip install flask
```
flask-socketio參考網址：https://flask-socketio.readthedocs.io/en/latest/  
安裝flask-socketio  
```程式語言=python
pip install flask-socketio
```
為了client能multi access至server必須使用eventlet  
參考網址:https://stackoverflow.com/questions/48611425/handle-concurrent-requests-or-threading-flask-socketio-with-eventlet  
安裝eventlet  
```程式語言=python
pip install eventlet
```
範例程式：webapp/video_demo.py  
匯入所需函式：  
```程式語言=python
import eventlet
eventlet.monkey_patch()
from eventlet import wsgi
from flask import Flask, request, abort, render_template, Response
from flask_socketio import SocketIO, emit
```
撰寫flask程式碼
```程式語言=python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def home():
    return render_template('index.html', async_mode=socketio.async_mode)

if __name__ == "__main__":
    wsgi.server(eventlet.listen(('0.0.0.0',5000)),app)
```
__socketIO會至目錄下的templates資料夾尋找html主體，請務必建立templates資料夾存放html檔，同時資源(如圖片)會存放至static資料夾中__  
範例程式：webapp/templates/index.html  
撰寫網頁主體，引入sockio相關程式碼  
```程式語言=html
<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
<script type="text/javascript" charset="utf-8">
    var socket = io();
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
</script>
```

# 步驟四：撰寫鏡頭/影片Streaming網站(結合模型辨識)
參考教學：https://blog.miguelgrinberg.com/post/video-streaming-with-flask  
參考程式碼：https://github.com/miguelgrinberg/flask-video-streaming  
## 影像處理
取用其中base_camera.py及camera_opencv.py兩隻程式進行更改  
base_camera.py中撰寫有基本鏡頭使用之程式，camera_opencv.py繼承base_camera進行改寫。  
範例程式：webapp/camera_opencv.py & webapp/video_opencv.py   
改寫camera_opencv.py：  
```程式語言=python
video_source = 0 #影像來源 0:Camera ; url:影片位置
P_left = 0 #計算偏左人數
P_right = 0 計算偏右人數

```
設值及取得計算人數
```程式語言=python
def get_person_count(source):
    return Camera.P_left,Camera.P_right


```
```程式語言=python
def set_person_count(l,r):
    Camera.P_left = l
    Camera.P_right = r

```
於frames()中參考上方測試模型之程式碼進行改寫。  

設定模型及影像來源：  
```程式語言=python
path = os.path.abspath('..')
model_path = path + "/person-detection-retail-0013.xml"
pbtxt_path = path + "/person-detection-retail-0013.bin"
net = cv2.dnn.readNet(model_path,pbtxt_path)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

camera = cv2.VideoCapture(Camera.video_source)
```
取得影像frames輸入模型：  
```程式語言=python
_, frame = camera.read()
img = cv2.resize(frame,(960,540))
blob = cv2.dnn.blobFromImage(img,size=(544,320))
net.setInput(blob)
out = net.forward()

```
劃出物件判斷框及計算人數:  
```程式語言=python
p_l = 0
p_r = 0
for detection in out.reshape(-1, 7):
   confidence = float(detection[2])
   xmin = int(detection[3] * img.shape[1])
   ymin = int(detection[4] * img.shape[0])
   xmax = int(detection[5] * img.shape[1])
   ymax = int(detection[6] * img.shape[0])

   if confidence > 0.5:
      xmin = int(detection[3] * img.shape[1])
      ymin = int(detection[4] * img.shape[0])
      xmax = int(detection[5] * img.shape[1])
      ymax = int(detection[6] * img.shape[0])
      if (img.shape[1]-xmax) > xmin:
           p_l = p_l +1
      else:
           p_r = p_r +1
      cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color=(0, 255, 0))
   Camera.set_person_count(p_l,p_r)
```
## flask
匯入上述程式:
```程式語言=python
import camera_opencv
```
撰寫影像輸出:
```程式語言=python
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

@app.route("/camera_feed")
def camera_feed():
    demo_cam = camera_opencv.Camera()
    return Response(gen(demo_cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

```
## Html
```程式語言=html
<h3>Camera</h3>
<img src="{{ url_for('camera_feed') }}">
```
# 步驟五：撰寫網頁控制GPIO功能
參考教學：https://randomnerdtutorials.com/raspberry-pi-web-server-using-flask-to-control-gpios/  
## flask
匯入RPi.GPIO:  
```程式語言=python
import RPi.GPIO as GPIO
```
宣告global變數用以人數統計，此變數用於步驟四之gen(camera)設值，並於接下來自動判斷的部分使用:  
```程式語言=python
P_left_count = 0
P_right_count = 0
```
參考步驟二教學設定需要之GPIO參數:
```程式語言=python
CONTROL_PIN = 17
PWM_FREQ = 50
GPIO.setmode(GPIO.BCM)
GPIO.setup(CONTROL_PIN, GPIO.OUT)
pwm = GPIO.PWM(CONTROL_PIN, PWM_FREQ)
pwm.start(0)

def angle_to_duty_cycle(angle=0):
   duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * int(angle) / 180)
   return duty_cycle
```
手動控制分三個動作:左、右及reset:
```程式語言=python
def action(angle):
   pwm.ChangeDutyCycle(angle_to_duty_cycle(int(angle)))
   return '',204

@app.route("/direction/reset")
def reset(angle):
   pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
   return '',204
```
自動控制則僅分為啟動及停止:
```程式語言=python
def auto():
   if P_left_count > P_right_count:
     pwm.ChangeDutyCycle(angle_to_duty_cycle(135))
   elif P_left_count < P_right_count:
     pwm.ChangeDutyCycle(angle_to_duty_cycle(45))
   else:
     pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
   return '',204
   
def stop():
   pwm.ChangeDutyCycle(angle_to_duty_cycle(90))

   return '',204
```
## HTML

分別以圖標作為GPIO控制按鈕:
```程式語言=html
<h3>Sign Control</h3>
<div>
<a href="/direction/45" role="button">
<img src="{{ url_for('static',filename='left-arrow.png')}}" width="50" height="50">
</a>
<img id="auto" src="{{ url_for('static',filename='auto.png')}}" width="50" height="50" onclick="changeStop()">
<a href="/stop" role="button">
<img id="stop" src="{{url_for('static',filename='stop.png')}}" width="50" height="50" onclick="changeAuto()">
</a>
<a href="/direction/90" role="button">
<img src="{{ url_for('static',filename='refresh.png')}}" width="50" height="50">
</a>
<a href="/direction/135" role="bitton">
<img src="{{ url_for('static',filename='arrow-point-to-right.png')}}" width="50" height="50">
</a>
</div>
```
javascript部分:  
以setInterval實現每五秒自動判斷告示牌指向
```程式語言= javascripy
<script type="text/javascript">
var setAuto;
function changeAuto(){
  clearInterval(setAuto);
  document.getElementById("stop").style.display = "none";
  document.getElementById("auto").style.display = "inline-block";
}
function changeStop() {
  setAuto = setInterval(function(){
    $.post("/auto",{});
  },5000);
  document.getElementById("auto").style.display = "none";
  document.getElementById("stop").style.display = "inline-block";
}
document.getElementById("stop").style.display = "none";
</script>
```
