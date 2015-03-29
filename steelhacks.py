# Etch and Sketch
#
# By:
# Anthony Kuntz
# Derrike Miller
# Roisin O'Dowd
#
# Uses juharris myo-python to interact with Myo and Oculus Rift


import myo
from myo.lowlevel import pose_t, stream_emg
from myo.six import print_
import random
import time
import math

from oculus import OculusListener
from oculus import oculusGo

from Tkinter import *

myo.init()

class Listener(myo.DeviceListener):
    # return False from any method to stop the Hub

    def __init__(self, canvas, hmd, hmdDesc, width, height): 
        self.width = width
        self.height = height
        self.position = (self.width/4, self.height/4) # Hardcoded starting position
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
        self.mainMenuTime = True
        self.bg = PhotoImage(file = "background.gif")
        #self.canvas.create_image(0,0,anchor=NW,image = self.bg)
        self.double = PhotoImage(file = "double.gif")
        self.logo = PhotoImage(file = "logo.gif")

        self.hmd = hmd
        self.hmdDesc = hmdDesc
        self.timerDelay = 50
        self.flashCount = 0
        self.v = 50
        self.dv = 7
        self.accelerate = True
        self.nwCorner = False
        self.rainbowTime = False
        self.rainbowColor = "red"
        self.count = 0
        self.lastYaw = 0
        self.squarePos = 52

    def rainbowColorChange(self):
        if self.colors.index(self.color) == (len(self.colors) - 1):
            self.color = self.colors[0]
        else:
            self.color = self.colors[self.colors.index(self.color) + 1]
        #self.color = self.colors[self.colors.index(self.color) + 1] if self.rainbowColor != "purple" else "red"
        self.rainbowColor = self.color
        


    def colorChange(self):
        if self.mainMenuTime: return
        # Cycles one step through the list of colors
        if self.rainbowTime:
            self.rainbowTime = False
            self.color = "black"
        elif self.color == "black":
            self.color = "red"
        elif self.color == "purple":
            self.rainbowTime = True
        else:
            self.color = self.colors[self.colors.index(self.color)+1]
        self.squarePos = (self.squarePos + 27) % (53 + 27*8 + 1)
        if self.squarePos < 52:
            self.squarePos = 52
        self.canvas.coords(self.squareLoc[0], self.width - 200, self.squarePos)
            # Pretty simple, just makes the color be the next one in the list of colors
        
    # def on_orientation_data(self, myo, timestamp, orientation):
    #     if self.mainMenuTime: return
    #     return

    #     for index in xrange(len(orientation)-1):
    #         if orientation[index] - self.previousOrientation[index] > .01:
    #             print index

    #     self.previousOrientation = orientation

    # From juharris myo-python
    def on_connect(self, myo, timestamp):
        print_("Connected to Myo")
        myo.vibrate('short') # This can be short, medium, or long
        myo.request_rssi()

    def on_sync(self, myo, timestamp, arm, x_direction):
        # ID on sync
        print arm
        print myo

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if self.mainMenuTime: return
        if self.rainbowTime:
            if timestamp - self.lastTimeStep > 1000000: # Checks for 1 million micro seconds
                self.lastTimeStep = timestamp
                self.rainbowColorChange()
            # Uncommenting the above makes the color change every second
        if not self.considerMyo: return # Don't draw if you shouldn't draw

        if self.horizontal:
            if gyroscope[0] > 10:
                try:
                    # Positive Rotation
                    self.position = (self.position[0] + 3, self.position[1]) if self.position[0] + 3 <= self.width else self.position
                    # Add to X value
                    self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                    # Determines width of line based on self.r variable
                    self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                    # Adds a pixel to our existing list of pixels!
                    self.listOfPositions.append((self.position[0], self.position[1], self.r))
                    # Adds the corresponding location
                except: pass

            elif gyroscope[0] < -10:
                try: # See above comments
                    self.position = (self.position[0] , self.position[1]+3) if self.position[1] + 3 <= self.height else self.position
                    self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                    self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                    self.listOfPositions.append((self.position[0], self.position[1], self.r))
                except: pass
        else:
            if gyroscope[0] > 10:
                try: # See above comments
                    self.position = (self.position[0], self.position[1]-3) if self.position[1] - 3 >= 0 else self.position
                    self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                    self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                    self.listOfPositions.append((self.position[0], self.position[1], self.r))
                except: pass

            elif gyroscope[0] < -10:
                try: # See above comments
                    self.position = (self.position[0]-3, self.position[1]) if self.position[0] - 3 >= 0 else self.position
                    self.otherPosition = (self.position[0] + self.r, self.position[1]+self.r)
                    self.listOfPixels.append(self.canvas.create_oval(self.position, self.otherPosition, fill = self.color, outline = self.color))
                    self.listOfPositions.append((self.position[0], self.position[1], self.r))
                except: pass


    def on_accelerometor_data(self, myo, timestamp, acceleration): 
        if self.mainMenuTime or not self.accelerate: return
        #show_output('acceleration', acceleration)
        # The above prints accelerometor data
        newValue = []
        for index in xrange(len(acceleration)):
           newValue.append(acceleration[index] - self.lastAcceleration[index])
        if abs(newValue[0]) > .1:
            self.r -= 10*int(round(newValue[0]/abs(newValue[0])))
            if self.r < 3: self.r = 3
        self.lastAcceleration = acceleration
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

    def translate(self, positive, direction):
        for index in xrange(len(self.listOfPixels)):
                try:
                    self.canvas.coords(self.listOfPixels[index], self.listOfPositions[index][0] + 100*positive*(direction == "x"), 
                                                                 self.listOfPositions[index][1] + 100*positive*(direction == "y"),
                                                                self.listOfPositions[index][0] + self.listOfPositions[index][2] + 100*positive*(direction == "x"), 
                                                                self.listOfPositions[index][1] + self.listOfPositions[index][2] + 100*positive*(direction == "y"))
                    self.listOfPositions[index] = (self.listOfPositions[index][0] + 100*positive*(direction=="x"), 
                        self.listOfPositions[index][1]+100*positive*(direction=="y"), self.listOfPositions[index][-1])
                # The above moves everything over
                except: continue

    def on_pose(self, myo, timestamp, pose):
        if self.mainMenuTime and pose == pose_t.double_tap:
            self.mainMenuTime = False
            self.canvas.delete(ALL)
            self.sidemenu = PhotoImage(file = "sidemenu.gif")
            self.canvas.create_image(self.width-200,0,anchor=NW,image = self.sidemenu)
            self.square = PhotoImage(file = "square.gif")
            self.squareLoc = []
            self.squareLoc.append(self.canvas.create_image(self.width-200, self.squarePos, image = self.square, anchor=NW))

        elif pose == pose_t.wave_in:
            self.canvas.delete(ALL)
            self.sidemenu = PhotoImage(file = "sidemenu.gif")
            self.canvas.create_image(self.width-200,0,anchor=NW,image = self.sidemenu)
            self.square = PhotoImage(file = "square.gif")
            self.squareLoc = []
            self.squareLoc.append(self.canvas.create_image(self.width-200, self.squarePos, image = self.square, anchor=NW))

            #self.position = (self.width/4, self.height/4)
            # The above makes the line stop drawing or resume drawing
            
        
            #self.position = (self.position[0] + 20, self.position[1])
            # Ignore the above
        elif pose == pose_t.fingers_spread: pass
        elif pose == pose_t.rest: pass
        elif pose == pose_t.fist: self.horizontal = not self.horizontal
        elif pose == pose_t.double_tap:
            self.colorChange()
            
            # Changes which direction you draw in

    def onTimerFired(self):
        if self.mainMenuTime:
            self.canvas.delete(ALL)
            self.v += self.dv
            if self.v < 50 or self.v > 190:
                self.dv *= -1
            self.canvas.create_rectangle(0,0,self.width,self.height,fill="mint cream")
            self.canvas.create_text(self.width/2, self.height/2, 
                text = "double tap to continue...", font = "CordiaNew 20", fill = rgbString(self.v, self.v, self.v))
            self.canvas.create_image(self.width/2, self.height*3/4.0, image = self.double)
            self.canvas.create_image(self.width/2, self.height/4, image = self.logo)
            

        # try: 
        #     yaw = oculusGo(self.hmd, self.hmdDesc)
        #     if abs(yaw - self.lastYaw) > .01:
        #         self.lastYaw = yaw
        #         4554
        #     if yaw - self.lastYaw == yaw == self.lastYaw == 0.0:
        #         #print "The Oculus is Broken :("
        #         #print ""
        #         pass

        # except: pass

    def onTimerFiredWrapper(self):
        self.onTimerFired()
        self.canvas.after(self.timerDelay, self.onTimerFiredWrapper)

    def onMousePressed(self, event):
        self.nwCorner = (event.x, event.y)

    def onKeyPressed(self, event):
        if self.nwCorner:
            if event.char.isalpha() or event.char in "?.,!:;/\\'@#$%^&*() ":
                self.canvas.create_text(self.nwCorner, text = event.char)
                self.nwCorner = (self.nwCorner[0] + 8, self.nwCorner[1])
        if event.keysym == "BackSpace":
            self.accelerate = not self.accelerate
        elif event.keysym == "Return":
            self.considerMyo = not self.considerMyo
        elif event.keysym == "Left":
            self.translate(-1, "x")
        elif event.keysym == "Right":
            self.translate(1, "x")
        elif event.keysym == "Up":
            self.translate(-1, "y")
        elif event.keysym == "Down":
            self.translate(1, "y")


def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

# From juharris myo-python
# Used primarily for debugging
def show_output(message, data):
    print_(message + ':' + str(data))
    # prints data for a given thing


def main():
    width = 1900
    height = 800
    timerDelay = 500
    root = Tk()
    root.resizable(True, True) # Change later?
    backgroundColor ="white" # For now
    canvas = Canvas(root, width = width,
        height = height, background = backgroundColor)
    canvas.pack() # Set up Canvas

    hub = myo.Hub()
    hub.set_locking_policy(myo.locking_policy.none)
    try:
        hmd, hmdDesc = OculusListener()
    except: pass
    try:
        listener = Listener(canvas, hmd, hmdDesc, width, height)
    except: listener = Listener(canvas, None, None, width, height)
    hub.run(1000, listener) # Listener for the Myo


    listener.onTimerFiredWrapper()

    def f(event): listener.onKeyPressed(event)
    root.bind("<Key>", f)

    def f(event): listener.onMousePressed(event)
    root.bind("<Button-1>", f)

    root.mainloop() # Halts program

if __name__ == '__main__':
  main()
