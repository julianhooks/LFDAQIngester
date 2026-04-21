from time import time

global lastTime = []

def enableTimer() -> int:
    lastTime.append(time())
    return len(lastTime) - 1

def getElapsedTime(timer:int) -> float:
    deltaTime = time() - lastTime[timer]
    lastTime[timer] = time()
    return deltaTime

def config() -> None:
    global timer1 = enableTimer()
    global timer2 = enableTimer()
    
    # create getElapsedTime() for use with counter based systems



