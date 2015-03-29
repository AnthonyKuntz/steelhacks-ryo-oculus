import time
from ovrsdk import *
import math

def OculusListener():

    ovr_Initialize()
    hmd = ovrHmd_Create(0)
    hmdDesc = ovrHmdDesc()
    ovrHmd_GetDesc(hmd, byref(hmdDesc))
    print hmdDesc.ProductName
    ovrHmd_StartSensor( \
        hmd, 
        ovrSensorCap_Orientation | 
        ovrSensorCap_YawCorrection, 
        0
    )
    return hmd, hmdDesc

def oculusGo(hmd, hmdDesc):
        ss = ovrHmd_GetSensorState(hmd, ovr_GetTimeInSeconds())
        pose = ss.Predicted.Pose
        yaw = math.asin(2*pose.Orientation.x*pose.Orientation.y
                      + 2*pose.Orientation.w*pose.Orientation.z)
        return yaw

        #( \
        #    pose.Orientation.w, 
        #    pose.Orientation.x, 
        #    pose.Orientation.y, 
        #    pose.Orientation.z
       # )
