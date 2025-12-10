import time
import math

from pymavlink import mavutil
def distancia (self,x,y):
    posX = self.position[0]
    posY = self.position[1]
    return math.sqrt ((x-posX)*(x-posX) + (y-posY)*(y-posY))
def prueba (self, x, y):
    result = self.getParams(["LOIT_SPEED"])
    print(result)
    normalLoiterSpeed = result[0]['LOIT_SPEED']
    loitSpeed = normalLoiterSpeed
    while True:
        d =  self.distancia (x,y)
        print ("Distancia: ", d )
        if d > 20 and loitSpeed != "RTL":
            self.setFlightMode ("RTL")
            print("RTL ")
            loitSpeed = "RTL"
            newParameters = [{'ID': "LOIT_SPEED", 'Value': normalLoiterSpeed}]
            self.setParams(newParameters)
        elif d > 15 and loitSpeed != 20:
            newParameters = [{'ID': "LOIT_SPEED", 'Value':20}]
            self.setParams(newParameters)
            loitSpeed = 20
            print("-------------------- ", 20)
        elif d > 12 and loitSpeed != 50:
            newParameters = [{'ID': "LOIT_SPEED", 'Value': 50}]
            self.setParams(newParameters)
            loitSpeed = 50
            print("-------------------- ", 50)
        elif d > 10 and loitSpeed != 100:
            newParameters = [{'ID': "LOIT_SPEED", 'Value': 100}]
            self.setParams(newParameters)
            loitSpeed = 100
            print("-------------------- ", 100)

        elif loitSpeed != normalLoiterSpeed:
            newParameters = [{'ID': "LOIT_SPEED", 'Value': normalLoiterSpeed}]
            self.setParams(newParameters)
            loitSpeed = normalLoiterSpeed
            print("-------------------- ", loitSpeed)

        time.sleep(0.2)