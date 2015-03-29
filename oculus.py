import time
from ovrsdk import *

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
        print "%10f   %10f   %10f   %10f" % ( \
            pose.Orientation.w, 
            pose.Orientation.x, 
            pose.Orientation.y, 
            pose.Orientation.z
        )
        time.sleep(0.016)
