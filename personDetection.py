import cv2
import time
import numpy as np
import imutils

model_path = "person-detection-retail-0013.xml"
pbtxt_path = "person-detection-retail-0013.bin"

net = cv2.dnn.readNet(model_path,pbtxt_path)


net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

#video = cv2.VideoCapture(0)

video = cv2.VideoCapture('demovideo1_Trim.mp4')
video.set(cv2.CAP_PROP_FRAME_WIDTH,640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

frameID = 0

grabbed = True

start_time = time.time()

while video.isOpened():
	grabbed,frame = video.read()
	img = cv2.resize(frame,(960,540))
	
	blob = cv2.dnn.blobFromImage(img,size=(544,320))
	net.setInput(blob)
	out = net.forward()
	
	
	p_right = 0
	p_left = 0
	for detection in out.reshape(-1, 7):

		confidence = float(detection[2])
		
		if confidence > 0.5:
			xmin = int(detection[3] * img.shape[1])
			ymin = int(detection[4] * img.shape[0])
			xmax = int(detection[5] * img.shape[1])
			ymax = int(detection[6] * img.shape[0])
			if (img.shape[1]-xmax) > xmin:
				p_left = p_left+1
			else:
				p_right = p_right+1
			cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color=(0, 255, 0))

	cv2.imshow("FRAME",img)
	print('left: %d'%p_left)
	print('right: %d'%p_right)
	
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

video.release()
cv2.destroyAllWindows()
