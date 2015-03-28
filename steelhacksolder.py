import myo
from myo.lowlevel import pose_t, stream_emg
from myo.six import print_
import random
import time
import math

from oculus import OculusListener

from Tkinter import *

myo.init()

class Listener(myo.DeviceListener):
    # return False from any method to stop the Hub

    def __init__(self, canvas): 
        self.position = (150,150) # Hardcoded starting position
        self.canvas = canvas
        self.horizontal = True # Alternates between drawing directions
        self.considerMyo = True # Turns of drawing 
        self.listOfPixels = [] # Everything that has been drawn
        self.listOfPositions = [] # Locations of those pixels
        self.lastAcceleration = [0,0,0]
        self.accelList = []
        self.accelAmountCap = 21 # When a Simpson's Rule happens
        self.colors = ["red","orange","yellow","green","cyan","blue","purple","black"]
        self.color = "black"
        self.r = 10 # Radius of line we draw
        self.lastTimeStep = 0
        self.previousOrientation = [0,0,0]

    def colorChange(self):
        # Cycles one step through the list of colors
        if self.color == "black":
            self.color = "red"
        else:
            self.color = self.colors[self.colors.index(self.color)+1]
            # Pretty simple, just makes the color be the next one in the list of colors
        
    def on_orientation_data(self, myo, timestamp, orientation):
        return

        for index in xrange(len(orientation)-1):
            if orientation[index] - self.previousOrientation[index] > .01:
                print index

        self.previousOrientation = orientation


    def on_connect(self, myo, timestamp):
        print_("Connected to Myo")
        myo.vibrate('short') # This can be short, medium, or long
        myo.request_rssi()

    def on_sync(self, myo, timestamp, arm, x_direction):
        # ID on sync
        print arm
        print myo

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if timestamp - self.lastTimeStep > 1000000: # Checks for 1 million micro seconds
            self.lastTimeStep = timestamp
            self.colorChange()
            # Uncommenting the above makes the color change every second
        if not self.considerMyo: return # Don't draw if you shouldn't draw

        if self.horizontal:
            if gyroscope[0] > 10:
                # Positive Rotation
                self.position = (self.position[0] + 3, self.position[1])
                # Add to X value
                self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                # Determines width of line based on self.r variable
                self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                # Adds a pixel to our existing list of pixels!
                self.listOfPositions.append((self.position[0], self.position[1], self.r))
                # Adds the corresponding location

            elif gyroscope[0] < -10: # See above comments
                self.position = (self.position[0] , self.position[1]+3)
                self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                self.listOfPositions.append((self.position[0], self.position[1], self.r))
        else:
            if gyroscope[0] > 10: # See above comments
                self.position = (self.position[0], self.position[1]-3)
                self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                self.listOfPositions.append((self.position[0], self.position[1], self.r))

            elif gyroscope[0] < -10: # See above comments
                self.position = (self.position[0]-3, self.position[1])
                self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                self.listOfPositions.append((self.position[0], self.position[1], self.r))


    def on_accelerometor_data(self, myo, timestamp, acceleration): 
        #show_output('acceleration', acceleration)
        # The above prints accelerometor data
        newValue = []
        for index in xrange(len(acceleration)):
           newValue.append(acceleration[index] - self.lastAcceleration[index])
        if abs(newValue[0]) > .1:
            self.r -= 10*int(round(newValue[0]/abs(newValue[0])))
        self.lastAcceleration =acceleration
        # If acceleration[2] is ever significant, the above conditional happens.
        # Currently, it does nothing

        ##### Integration Stuff #####

        # self.accelList.append(acceleration)
        # if len(self.accelList) == self.accelAmountCap:
        #     newtime = time.time()
        #     difference = newtime - self.time
        #     step = difference / self.accelAmountCap
        #     total = 0
        #     for index in xrange(len(self.accelList)):
        #         value = (self.accelList[index][2])*9.81
        #         if index == 0 or index == len(self.accelList) - 1: total += value
        #         elif index % 2 == 1: total += 4*value
        #         else: total += 2*value
        #     total *= (step / 3.0)
        #     distance = total * difference / 2
            
        #     if distance > .001:
        #         print distance, "Distance!"
        #         newPosition = (self.position[0] + distance*500, self.position[1])
        #         self.canvas.create_line(self.position, newPosition)
        #         self.position = newPosition
        #     self.accelList = []
        # self.time = time.time()

        ##############
        # The above is our old attempt at accelerometor --> positon via integration
        ##############

    def on_pose(self, myo, timestamp, pose):
        print pose
        if pose == pose_t.wave_out:
            myo.vibrate('short')
            #self.considerMyo = not self.considerMyo
            # The above makes the line stop drawing or resume drawing
            self.colorChange()
        elif pose == pose_t.double_tap:
            print "hi"
            for index in xrange(len(self.listOfPixels)):
                self.canvas.coords(self.listOfPixels[index], self.listOfPositions[index][0] + 20, 
                                                             self.listOfPositions[index][1],
                                                            self.listOfPositions[index][0] + self.listOfPositions[index][-1] + 20, 
                                                            self.listOfPositions[index][1] + self.listOfPositions[index][-1])
                self.listOfPositions[index] = (self.listOfPositions[index][0] + 20, self.listOfPositions[index][1], self.listOfPositions[index][-1])
                # The above moves everything over
            #self.position = (self.position[0] + 20, self.position[1])
            # Ignore the above
        elif pose == pose_t.wave_in: pass
        elif pose == pose_t.rest: pass
        elif pose == pose_t.fingers_spread: self.horizontal = not self.horizontal
        elif pose == pose_t.fist:
            print "fist"
            myo.vibrate('short')
            
            # Changes which direction you draw in



def show_output(message, data):
    print_(message + ':' + str(data))
    # prints data for a given thing


def main():
    width = 1500
    height = 800
    root = Tk()
    root.resizable(True, True) # Change later?
    backgroundColor ="white" # For now
    canvas = Canvas(root, width = width,
        height = height, background = backgroundColor)
    canvas.pack() # Set up Canvas

    hub = myo.Hub()
    hub.set_locking_policy(myo.locking_policy.none)

    hub.run(1000, Listener(canvas)) # Listener for the Myo

    #OculusListener()

    # Set up our Oculus listener(canvas)

    def f(event): onKeyPressed(event)
    root.bind("<Key>", f)

    root.mainloop() # Halts program

def onKeyPressed(event):
    print "hi"


if __name__ == '__main__':
   main()
