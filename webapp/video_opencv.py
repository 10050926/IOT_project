import os
import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    path = os.path.abspath('..')
    video_source = path + '/demovideo1_Trim.mp4'
    P_left = 0
    P_right = 0

    def __init__(self):
                super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    def get_person_count(source):
        return Camera.P_left,Camera.P_right

    def set_person_count(l,r):
        Camera.P_left = l
        Camera.P_right = r

    @staticmethod
    def frames():
        model_path = path + "/person-detection-retail-0013.xml"
        pbtxt_path = path + "/person-detection-retail-0013.bin"
        net = cv2.dnn.readNet(model_path,pbtxt_path)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

        camera = cv2.VideoCapture(Camera.video_source)
        

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while camera.isOpened():
            # read current frame
            _, frame = camera.read()
            img = cv2.resize(frame,(960,540))
            blob = cv2.dnn.blobFromImage(img,size=(544,320))
            net.setInput(blob)
            out = net.forward()

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
            # encode as a jpeg image and return it
               Camera.set_person_count(p_l,p_r)

            yield cv2.imencode('.jpg', img)[1].tobytes()
