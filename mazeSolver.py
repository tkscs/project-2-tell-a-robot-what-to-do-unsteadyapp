grid = []
x = 8
import numpy as np
for i in range(0,x):
    grid.append("o" * int(x))
where = (0,0)
goal = (3,3)
direction = 0
def createMap():
    mapping = grid.copy()
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            mapping[i] = mapping[i][:j] + str(np.abs(j - goal[0]) + np.abs(i-goal[1])) + mapping[i][j+1:]
    return(mapping)
def sonarScan():
    return(False)
def forward():
    # put whatever forward code here
    global where
    where = (int(where[0]+np.round(np.sin((direction*np.pi)/180))),int(where[1]+np.round(np.cos((direction*np.pi)/180))))
    print(where)
end = False
currentMap = createMap()
print(currentMap)
def angleCalculate(start,destination):
    rotate(start-destination)
def rotate(angle):
    global direction
    direction = direction + angle
    #for later
testing = (int(where[0]+np.round(np.sin((direction*np.pi)/180))),int(where[1]+np.round(np.cos((direction*np.pi)/180))))
while end == False:
    values = []
    value = [100000,"imposible"]
    for p in [(1,0),(-1,0),(0,1),(0,-1)]:
        whereTo = np.array(where) + np.array(p)
        whereTo = [int(whereTo[0]),int(whereTo[1])]
        print("the coords" + str(whereTo))
        if(whereTo[0] < 8 and whereTo[1] < 8 and whereTo[0] > -1 and whereTo[1] > -1):
            print("coord " + str((p[0],p[1])) + ". Value: " + str(value[0]) + ". Map" + str(int(currentMap[whereTo[1]][whereTo[0]])))
            if(value[0] > int(currentMap[whereTo[1]][whereTo[0]])):
                value[0] = int(currentMap[whereTo[1]][whereTo[0]])
                value[1] = round(180 * np.atan2(p[1],p[0])/np.pi)
                print("angle" + str(value[1]))
            values.append([currentMap[whereTo[1]][whereTo[0]],direction])
    if(value[1] == "imposible"):
        print(value)
        raise Exception("no space to move!")
    angleCalculate(direction,value[1])
    print("moved" + str(where))
    forward()
    currentMap = createMap()
    if(where == goal):
        end = True