from simulator import robot, FORWARD, BACKWARD, STOP
import time
import random
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
    if(angle%360 == 0):
        debugDirrection = None
        angleInSeconds = 0
    elif(angle%360<=180):
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
def forward(dist): #comment
    """Distance to go: Float"""
    print(dist)
    print(speed_per_power_in_seconds)
    print(dist/speed_per_power_in_seconds)
    motorsAndWait(FORWARD,FORWARD,dist/speed_per_power_in_seconds)
    print(f"done {dist/speed_per_power_in_seconds}")
def sign(num):
    """Number: Float
    Returns : 1,-1"""
    if(num>=0):
        return(1)
    else:
        return(-1)
#technicly 899 but as soon as it rotates it will crash
#200 x 200
# functionaly 100 * (2**1/2)
inp = False
while True:
    print(robot.driver.x,robot.driver.y)
    vector = (1000-(100 * (2**(1/2))),random.randint(-300,300))
    vector = (1001-(100 * (2**(1/2))),0)
    if(inp):
        userInp = input("Left or Right").lower()
        if(userInp == "left"):
            print("not working right now, bye")
            quit()
        elif(userInp == "right"):
            userInp = input("x coord").lower()
            try:
                if(userInp>0):
                    vector[0] = userInp
            except TypeError:
                print("not a number, using default")
        else:
            print("that's not either")
            quit()
    print(robot.left_sonar())
    print(vector)
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
    angleToRotateTo = toAdd + (angleInRad*180/np.pi)
    AdvancedRotateTo(angleToRotateTo)
    #distance = np.linalg.norm(vector)
    distance = (vector[0]**2 + vector[1]**2)**(1/2)
    sonarDist = robot.left_sonar()*10
    if(sonarDist-(100 * (2**(1/2)))>distance):
        raise Exception(f"Too close!, {sonarDist-(100 * (2**(1/2)))} is greater than {distance}")
    forward(distance)
    rotateTo(180)
    forward(distance)
    AdvancedRotateTo((180 - (angleToRotateTo%360))%360)
    if(robot.driver.x != 0 or robot.driver.y != 0 or robot.driver.heading != 0):
        print("Not at origin: ",robot.driver.x,robot.driver.y,robot.driver.heading)
    
