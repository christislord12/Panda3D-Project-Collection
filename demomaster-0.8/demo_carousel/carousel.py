
from random import randint, random
import math, sys, colorsys, threading
from math import pi, sin

#import direct.directbase.DirectStart
from pandac.PandaModules import Filename
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
from pandac.PandaModules import Material
from direct.interval.IntervalGlobal import *   #Needed to use Intervals
from pandac.PandaModules import NodePath, WindowProperties
##from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3

import demobase

####################################################################################################################
class CarouselDemo(demobase.DemoBase):
    """
    Misc - Carousel
    Just the carousel demo from the tutorial.
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.LoadModels()
        self.startCarousel()

    def LoadModels(self):
        self.SetCameraPosHpr(0, -8, 2.5, 0, -9, 0)
        base.setBackgroundColor(.6, .6, 1) #Set the background color
        base.disableMouse()                #Allow manual positioning of the camera

        self.carousel = loader.loadModel("models/carousel_base")
        self.carousel.reparentTo(render)   #Attach it to render

        #Load the modeled lights that are on the outer rim of the carousel
        #(not Panda lights)
        #There are 2 groups of lights. At any given time, one group will have the
        #"on" texture and the other will have the "off" texture.
        self.lights1 = loader.loadModel("models/carousel_lights")
        self.lights1.reparentTo(self.carousel)

        #Load the 2nd set of lights
        self.lights2 = loader.loadModel("models/carousel_lights")
        #We need to rotate the 2nd so it doesn't overlap with the 1st set.
        self.lights2.setH(36)
        self.lights2.reparentTo(self.carousel)

        #Load the textures for the lights. One texture is for the "on" state,
        #the other is for the "off" state.
        self.lightOffTex = loader.loadTexture("models/carousel_lights_off.jpg")
        self.lightOnTex = loader.loadTexture("models/carousel_lights_on.jpg")

        #Create an list (self.pandas) with filled with 4 dummy nodes attached to
        #the carousel.
        #This uses a python concept called "Array Comprehensions." Check the Python
        #manual for more information on how they work
        self.pandas = [self.carousel.attachNewNode("panda"+str(i))
                       for i in range(4)]
        self.models = [loader.loadModelCopy("models/carousel_panda")
                       for i in range(4)]
        self.moves = [0 for i in range(4)]

        for i in range(4):
          #set the position and orientation of the ith panda node we just created
          #The Z value of the position will be the base height of the pandas.
          #The headings are multiplied by i to put each panda in its own position
          #around the carousel
          self.pandas[i].setPosHpr(0, 0, 1.3, i*90, 0, 0)

          #Load the actual panda model, and parent it to its dummy node
          self.models[i].reparentTo(self.pandas[i])
          #Set the distance from the center. This distance is based on the way the
          #carousel was modeled in Maya
          self.models[i].setY(.85)

        #Load the environment (Sky sphere and ground plane)
        self.env = loader.loadModel("models/env")
        self.env.reparentTo(render)
        self.env.setScale(7)
        self.env.setLightOff()

        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .35, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_directionalLight = demobase.Att_directionalLightNode(False,"Light:Directional Light",Vec4( .9, .8, .9, 1 ) ,Vec3( 0, 8, -2.5 ) )
        self.att_directionalLight.setLight(render)

        #self.att_spotLight = demobase.Att_spotLightNode(False, "Light:Spotlight",  Vec4( .45, .45, .45, 1 ), 16, 60.0, Vec3(0,0,0), Point3(0,0,0), attenuation=Vec3( 1, 0.0, 0.0 ), node=camera)
        #self.att_spotLight.setLight(render)

    def startCarousel(self):
        #Here's where we actually create the intervals to move the carousel
        #The first type of interval we use is one created directly from a NodePath
        #This interval tells the NodePath to vary its orientation (hpr) from its
        #current value (0,0,0) to (360,0,0) over 20 seconds. Intervals created from
        #NodePaths also exist for position, scale, color, and shear

        self.carouselSpin = self.carousel.hprInterval(20, Vec3(360, 0, 0))
        #Once an interval is created, we need to tell it to actually move.
        #start() will cause an interval to play once. loop() will tell an interval
        #to repeat once it finished. To keep the carousel turning, we use loop()
        self.carouselSpin.loop()

        #The next type of interval we use is called a LerpFunc interval. It is
        #called that becuase it linearly interpolates (aka Lerp) values passed to
        #a function over a given amount of time.

        #In this specific case, horses on a carousel don't move contantly up,
        #suddenly stop, and then contantly move down again. Instead, they start
        #slowly, get fast in the middle, and slow down at the top. This motion is
        #close to a sine wave. This LerpFunc calls the function oscilatePanda
        #(which we will create below), which changes the hieght of the panda based
        #on the sin of the value passed in. In this way we achieve non-linear
        #motion by linearly changing the input to a function
        for i in range(4):
              self.moves[i] = LerpFunc(
                              self.oscilatePanda,  #function to call
                              duration = 3,  #3 second duration
                              fromData = 0,  #starting value (in radians)
                              toData = 2*pi, #ending value (2pi radians = 360 degrees)
                                             #Additional information to pass to
                                             #self.oscialtePanda
                              extraArgs=[self.models[i], pi*(i%2)]
                              )
              #again, we want these to play continuously so we start them with loop()
              self.moves[i].loop()

        #Finally, we combine Sequence, Parallel, Func, and Wait intervals,
        #to schedule texture swapping on the lights to simulate the lights turning
        #on and off.
        #Sequence intervals play other intervals in a sequence. In other words,
        #it waits for the current interval to finish before playing the next
        #one.
        #Parallel intervals play a group of intervals at the same time
        #Wait intervals simply do nothing for a given amount of time
        #Func intervals simply make a single function call. This is helpful because
        #it allows us to schedule functions to be called in a larger sequence. They
        #take virtually no time so they don't cause a Sequence to wait.

        self.lightBlink = Sequence(
          #For the first step in our sequence we will set the on texture on one
          #light and set the off texture on the other light at the same time
          Parallel(
            Func(self.lights1.setTexture, self.lightOnTex, 1),
            Func(self.lights2.setTexture, self.lightOffTex, 1)),
          Wait(1), #Then we will wait 1 second
          #Then we will switch the textures at the same time
          Parallel(
            Func(self.lights1.setTexture, self.lightOffTex, 1),
            Func(self.lights2.setTexture, self.lightOnTex, 1)),
          Wait(1)  #Then we will wait another second
        )

        self.lightBlink.loop() #Loop this sequence continuously


    def oscilatePanda(self, rad, panda, offset):
        #This is the oscillation function mentioned earlier. It takes in a degree
        #value, a NodePath to set the height on, and an offset. The offset is there
        #so that the different pandas can move opposite to each other.
        #The .2 is the amplitude, so the height of the panda will vary from -.2 to
        #.2
        panda.setZ(sin(rad + offset) * .2)

    def ClearScene(self):
        self.lightBlink.finish()
        for i in range(4):
              self.moves[i].finish()

        base.camera.detachNode()
        #render.clearShaderInput('light')
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

