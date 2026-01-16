from simulator import robot, FORWARD, BACKWARD, STOP
import time
degreesPerFrame = 0.98
fps = 60
heading = 0
speed_per_power_in_seconds = 60
heading = (heading + degreesPerFrame) % 360

def rotate(angle):
    angleInSeconds = angle/(0.98 * 60)
    # angle = 0.98 * 60 * seconds
    #seconds = angle/(0.98 * 60)
    motorsAndWait(BACKWARD,FORWARD,angleInSeconds)
def motorsAndWait(Left,Right,Seconds):
    robot.motors(left=Left,right=Right,seconds=Seconds)
    time.sleep(Seconds)

time.sleep(100)
robot.exit()