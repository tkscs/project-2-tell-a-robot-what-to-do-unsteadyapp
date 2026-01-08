from simulator import robot, FORWARD, BACKWARD, STOP
import time
import random
import numpy as np
debug = False
def rotateTo(angle):
    """Simple version, only rotates to the left \n
    Angle is a postive float to rotate that many degrees"""
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
    """calls the motors for the specified time \n
    left = FORWARD, BACKWARD, STOP \n
    right = FORWARD, BACKWARD, STOP \n
    seconds =float>0.5"""
    if(Seconds<0.5):
        motorsAndWait(Left,Right,Seconds=Seconds+0.5)
        motorsAndWait(inverseOf(Left),inverseOf(Right),Seconds=0.5)
        print("broke, less than 0.5")
    else:
        ModSeconds = Seconds
        robot.motors(left=Left,right=Right,seconds=ModSeconds)
def inverseOf(bit):
    if(bit == FORWARD):
        return(BACKWARD)
    elif(bit== BACKWARD):
        return(FORWARD)
    else:
        return(STOP)
def forward(dist): #comment
    """Distance to go: Float"""
    print(dist)
    print(speed_per_power_in_seconds)
    print(dist/speed_per_power_in_seconds)
    motorsAndWait(FORWARD,FORWARD,dist/speed_per_power_in_seconds)
    print(f"done {dist/speed_per_power_in_seconds}")
def sign(num):
    """Number: Float \n
    Returns : 1,-1"""
    if(num>=0):
        return(1)
    else:
        return(-1)
#technicly 899 but as soon as it rotates it will crash
#200 x 200
# functionaly 100 * (2**1/2)
inp = False
EXTRADISTANCEWHILETURNED = (100 * (2**(1/2))) - 100 #about 44
while True:
    if(debug):
        print(robot.driver.x,robot.driver.y)
    vector = [1000-(100 * (2**(1/2))),random.randint(-300,300)]
    vector = [899-EXTRADISTANCEWHILETURNED,random.randint(-500,500)]
    userInp = input("go back after moving? (assumed true unless you type \"no\")").lower().strip()
    if(userInp == "no"):
        goBack = False
    else:
        goBack = True
    rotateAfter = None
    while rotateAfter == None:
        userInp = input("Left, Right, or quit").lower().strip()
        if(userInp == "left"):
            try:
                userInp = int(input("y coord").lower().strip())
            except TypeError:
                print("not a number, using default")
            else:
                if(userInp<300 and userInp>-300):
                    vector[1] = userInp
                    rotateAfter = True
                    if(debug):
                        time.sleep(1)
                    AdvancedRotateTo(180)
                else:
                    print(f"{userInp} is not between -300 and 300")
        elif userInp == "quit":
            quit()
        elif(userInp == "right"):
            try:
                userInp = int(input("y coord").lower().strip())
            except TypeError:
                print("not a number, using default")
            else:
                if(userInp<300 and userInp>-300):
                    vector[1] = userInp
                    rotateAfter = False
                else:
                    print(f"{userInp} is not between -300 and 300")
    else:
            print("that's not either")
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
    time.sleep(0.1)
    AdvancedRotateTo(angleToRotateTo)
    time.sleep(0.1)
    distance = (vector[0]**2 + vector[1]**2)**(1/2)
    print(f"dist:{distance}")
    rightSonar = robot.right_sonar() * 10
    time.sleep(0.5)
    leftSonar = robot.left_sonar() * 10
    sonarDist = max(leftSonar,rightSonar)
    if(sonarDist<distance - EXTRADISTANCEWHILETURNED):
        raise Exception(f"Too close!, {sonarDist} is greater than {distance + EXTRADISTANCEWHILETURNED}")
    else:
        print(f"Sonar distance: {sonarDist}, while want to go = {distance}")
    forward(distance)
    rotateTo(180)
    if(goBack):
        forward(distance)
    AdvancedRotateTo(((180*rotateAfter) + 180 - (angleToRotateTo%360))%360)
    if(debug):
        if(robot.driver.x != 0 or robot.driver.y != 0 or robot.driver.heading != 0):
            print("Not at origin: ",robot.driver.x,robot.driver.y,robot.driver.heading)