import socket
from _thread import *
import threading
import random
from model import Data
import pickle
import csv
from ControlTransfer import Orchestrate
import sys
from RepeatedTimer import *
from CloudStatus import *
numberOfUser = int(sys.argv[1])
connectionPool=dict()
orchestrate=dict()
def orchestrator(orchestrate,pingSocket): # first parameter hold the current  routing decision and secon is the stack that periodically hold the response return by the  cloud server in terms of cloud running performance
  
  pingSocket.send("ping".encode("utf-8"))
  bytesReceived=pingSocket.recv(1024)
  currentInstance=pickle.loads(bytesReceived)
  print(currentInstance.instancePerformance)
  for user, orcha in orchestrate.items():
    orcha.atEdge=not orcha.atEdge
  #print(orchestrate)

def createClientSocket(host,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    return s

def readInstanceInfo(fileName):
 with open(fileName) as f:
    next(f)  # Skip the headeri
    tupleTemp=[]
    reader = csv.reader(f, skipinitialspace=True)
    for row in reader:
     resolution = row[0] 
     startPort = row[1]
     instances=row[2]
     tupleTemp.append(tuple([resolution,[startPort,instances]]))
    return dict(tupleTemp)

def createChannelForUser(userId):
 dedicatedPool=dict()
 for resolution, socket in connectionPool.items():
    dedicatedPool[resolution]=socket[userId]
 return dedicatedPool

def createNewSocketConnection(host,portt):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, portt))
        s.listen(10)
        return s

def sendForComputation(socket,frameSize, imgByte):
  socket.send(frameSize)
  status=socket.recv(1024).decode("utf-8")
  socket.send(imgByte)
  return socket.recv(1024)
  
def interfaceCamera(port,dedicatedConnections,orchra,cloudHost, cloudPort):
    offload = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    offload.connect((cloudHost,cloudPort))
    print("camera are expected at port",port)
    s=createNewSocketConnection('0.0.0.0',port)
    while(True):
     c, addr = s.accept()
     while True:
      try:
        frameSize = c.recv(1024)
        imageLength= int(frameSize.decode("utf-8"))
        c.send((str('True')).encode("utf-8"))
        i=0
        chunk=b''
        while(i!=imageLength):
         imgByte= c.recv(1024)
         chunk=chunk+imgByte
         i=i+len(imgByte)
        if(orchra.atEdge):
         connectionToUse=orchra.resolution
         dataResult=sendForComputation(dedicatedConnections[orchra.resolution],frameSize,chunk)
        else:
         data=Data(orchra.resolution,chunk)
         stream=pickle.dumps(data)
         length=str(len(stream)).encode("utf-8")
         dataResult=sendForComputation(offload,length,stream)
        c.send("Helloworld".encode("utf-8"))
      except:
       break
def Main(numberOfUser):
 host='127.0.0.1'
 cloudHost='40.76.192.181'
 cloudPort=9090
 cloudControlPort=9080
 instanceInfo=readInstanceInfo('config.csv')
 for resolution,portConfig in instanceInfo.items():
  initialPort=int(portConfig[0])
  pool=[]
  for counter in range(0, int(portConfig[1])):
   connectorPort=initialPort+counter
   socket=createClientSocket('127.0.0.1',connectorPort)
   pool.append(socket)
  connectionPool[resolution]=pool
 userPort=9000
 for user in range(0,numberOfUser):
  dedicatedConnections=createChannelForUser(user)
  orchra=Orchestrate('a',False)
  orchestrate[user]=orchra
  start_new_thread(interfaceCamera,(userPort,dedicatedConnections,orchra,cloudHost,cloudPort))
  userPort=userPort+1
  cloudPort=cloudPort+1
 pingSocket=createClientSocket(cloudHost,cloudControlPort)
 backGroundProcess = RepeatedTimer(10, orchestrator, orchestrate,pingSocket)
 print("Initilization completed") 
 input()
# for key, value in connectionPool.items():

#  for sock in value:
 #   sock.close()

if __name__ == '__main__':
    Main(numberOfUser)
