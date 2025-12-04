from simulator import robot, FORWARD, BACKWARD, STOP
import time
import pynput
import numpy as np
class robotExtras():
    pos = (0,0)
    goal = None
    direction = 0
def onClick(coords):
    if(coords>0):
        robotExtras.goal = coords
def rotateTo(angle):
    angleInSeconds = (angle)/(0.98 * 60)
    motorsAndWait(FORWARD,BACKWARD,abs(angleInSeconds))
def AdvancedRotateTo(angle):
    if(angle%360<=180):
        angleInSeconds = (angle)/(0.98 * 60)
        debugDirrection = "right"
        motorsAndWait(FORWARD,BACKWARD,abs(angleInSeconds))
    else:
        angleInSeconds = (180-(angle%180))/(0.98 * 60)
        debugDirrection = "left"
        motorsAndWait(BACKWARD,FORWARD,abs(angleInSeconds))
    print(f"angle: {angle} converted to {angleInSeconds} while turning to the {debugDirrection}")
def motorsAndWait(Left,Right,Seconds):
    robot.motors(left=Left,right=Right,seconds=Seconds)
    time.sleep(Seconds)
vector = (-200,-200)
def sign(num):
    if(num>=0):
        return(1)
    else:
        return(-1)
signX = sign(vector[0]) == 1
signY = sign(vector[1]) == 1
if(signX and signY):
    toAdd = 0
    inverse = False
    vector = (abs(vector[0]),abs(vector[1]))
elif(not(signX) and not(signY)):
    toAdd = 180
    inverse = False
    vector = (abs(vector[0]),abs(vector[1]))
elif(not(signX) and signY):
    toAdd = 90
    inverse = True
    vector = (abs(vector[1]),abs(vector[0]))
elif(signX and not(signY)):
    toAdd = 270
    inverse = True
    vector = (abs(vector[1]),abs(vector[0]))
else:
    raise Exception("Signs don't meet any conditions")

speed_per_power_in_seconds = 60
try:
    angleInRad = (np.arctan(vector[1]/vector[0]))
except ZeroDivisionError:
    angleInRad = np.pi
print(toAdd + (angleInRad*180/np.pi))
AdvancedRotateTo(toAdd + (angleInRad*180/np.pi))
distance = np.linalg.norm(vector)
print(distance)
def forward(dist):
    motorsAndWait(FORWARD,FORWARD,dist/speed_per_power_in_seconds)
    print("done")
forward(distance)
print(distance)
input()