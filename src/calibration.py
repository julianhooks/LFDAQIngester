from time import time

global lastTime 
lastTime = []

def enableTimer() -> int:
    lastTime.append(time())
    return len(lastTime) - 1

def getElapsedTime(timer:int) -> float:
    deltaTime = time() - lastTime[timer]
    lastTime[timer] = time()
    return deltaTime