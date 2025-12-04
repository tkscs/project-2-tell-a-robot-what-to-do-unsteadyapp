from simulator import robot, FORWARD, BACKWARD, STOP
import time as t
time = 10
robotSpeed = 1 #constant
def forward(time):
    from_to_wall=robot.left_sonar()
    print(from_to_wall)
    if(robotSpeed*time > from_to_wall):
        time = from_to_wall/robotSpeed
    print(time)
    robot.motors(FORWARD,FORWARD,time)
forward(100)
t.sleep(10)