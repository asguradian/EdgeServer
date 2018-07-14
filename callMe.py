from time import sleep
from RepeatedTimer import *
def hello(name):
    print ("Hello %s!", name)

print ("starting...")
rt = RepeatedTimer(10, hello, "World") # it auto-starts, no need of rt.start()
try:
 input()
finally:
    rt.stop() # better in a try/finally block to make sure the program ends!
