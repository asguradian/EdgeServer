# import socket programming library
import socket
import sys 
# import thread module
from _thread import *
import threading
from queue import *
import random
from darkflow.net.build import TFNet
import json
import base64
import numpy as np
import cv2
import math
import time
import copy
from PIL import Image
#port = sys.argv[1]
#dataPort=sys.argv[2]
#serverPort=sys.argv[3]
# thread fuction
def convertDetectionToNumpy(jsonDetection=None):
    person_info=[] #holds the detections information in the form of array.
    for detection in jsonDetection:
       confidence= detection['confidence']
       label=detection['label']
       topleftX= np.floor(detection['topleft']['x']).astype('int32')
       topleftY=np.floor(detection['topleft']['y']).astype('int32')
       bottomrightX= np.floor(detection['bottomright']['x']).astype('int32')
       bottomrightY = np.floor(detection['bottomright']['y']).astype('int32')
       boundingBoxWidth= math.sqrt(math.pow(bottomrightX-topleftX,2)+math.pow(bottomrightY-topleftY,2))
       if(label=='person' and boundingBoxWidth>80): #consider detections from which features could be extracted.
        person_info.append((str(topleftX),str(topleftY),str(bottomrightX-topleftX),str(bottomrightY-topleftY),str(confidence)))
    return person_info

def orchestrator(c,tfnet):
    while True:
        frameSize = c.recv(1024)
 #       print("received from socket",frameSize)
        imageLength= int(frameSize.decode("utf-8"))
        c.send((str('True')).encode("utf-8"))
        i=0
        chunk=b''
        while(i!=imageLength):
         imgByte= c.recv(1024)
         chunk=chunk+imgByte
         i=i+len(imgByte)
        imgcv= base64.b64decode(chunk)
        imrr=np.fromstring(imgcv, np.uint8)
        img_np = cv2.imdecode(imrr, 1)
        an=tfnet.return_predict(img_np)
#        print(an)
        c.send("Helloworld".encode("utf-8"))

def createClientSocket(port,host):
    print("Connected to Remote Server")
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port)) 
    return s
def createNewSocketConnection(host,portt): 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   #     s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind((host, portt))
        s.listen(10)
        print("Next available Data Port:",host,portt)
        return s






def Main():
    host='0.0.0.0'
    queue=Queue()
    dis=dict()
    data=[]
    portt=8081
    np_frame =cv2.imread("test.jpg")
    options = {"model": "cfg/yolo.cfg", "load": "bin/yolo.weights", "threshold": 0.6,"gpu":0.1,"labels":"labels.txt"}
    for i in (0,1,2,3,4):
     tfnet = TFNet(options)
     an=tfnet.return_predict(np_frame)
     data.append(tfnet)
     print("Hello World")
  #  s.send((str(byteLength)).encode("utf-8"))
    #print("Hello World")
    try:
        while 1:
                s=createNewSocketConnection(host,portt)
                conn, addr = s.accept()
                print( '[*] Connected with ' + addr[0] + ':' + str(addr[1]))
                start_new_thread(orchestrator,(conn,data[0]))
                portt=portt+10
            

    except KeyboardInterrupt as msg:
        sys.exit(0)

if __name__ == '__main__':
    Main()
