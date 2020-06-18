from random import randint, random
import math, sys, colorsys, threading
from math import pi, sin

#import direct.directbase.DirectStart
from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
from pandac.PandaModules import Material
from direct.interval.IntervalGlobal import *   #Needed to use Intervals
from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3

import demobase

#Global variables for the tunnel dimensions and speed of travel
TUNNEL_SEGMENT_LENGTH = 50
TUNNEL_TIME = 1   #Amount of time for one segment to travel the
                  #distance of TUNNEL_SEGMENT_LENGTH

####################################################################################################################
class TunnelDemo(demobase.DemoBase):
    """
    Fog - Tunnel with a test shader
    The tunnel demo from the tutorial, with my fog shader
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.att_sync = demobase.Att_Boolean(False, "Synchronize Fog and background color", True)
        self.SetCameraPosHpr(0,0,10, 0, -90, 0)
        self.att_backgroundcolor = demobase.Att_backgroundColor(False,"Background Color", Vec4(0, 0, 0,1))
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(1,1,1, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_ambientLight.setNotifier(self.changeambientLight)

        self.att_usemyfog = demobase.Att_Boolean(False, "Use my fog shader", False)
        self.att_usemyfog.setNotifier(self.usemyfog)

        self.att_fog = demobase.Att_exponentialFog(False, "Exponential Fog", Vec4(0,0,0,1), 0.08)
        self.att_fog.setFog(render)
        base.disableMouse()                #Allow manual positioning of the camera
        self.LoadModels()

        self.att_fog.setNotifier(self.fogchange)
        self.att_backgroundcolor.setNotifier(self.backgroundchange)

    def fogchange(self, object):
        if self.att_sync.v:
            self.att_backgroundcolor.setColor(None, self.att_fog.att_color.getColor())
        if self.att_usemyfog.v:
            #render.setShaderInput('alight0', self.att_ambientLight.light)
            render.setShaderInput('fogDensity', self.att_fog.att_expDensity.v, 0, 0, 0)
            render.setShaderInput('fogColor', self.att_fog.att_color.getColor())


    def backgroundchange(self, object):
        if self.att_sync.v:
            self.att_fog.setColor(None, self.att_backgroundcolor.att_color.getColor())

    def changeambientLight(self, object):
        if self.att_usemyfog.v:
            render.setShaderInput('alight0', self.att_ambientLight.light)

    def LoadModels(self):

        #Load the tunel and start the tunnel
        self.initTunnel()

#        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .35, 1 ))
#        self.att_ambientLight.setLight(render)
#        self.att_directionalLight = demobase.Att_directionalLightNode(False,"Light:Directional Light",Vec4( .9, .8, .9, 1 ) ,Vec3( 0, 8, -2.5 ) )
#        self.att_directionalLight.setLight(render)


    def initTunnel(self):
        #Creates the list [None, None, None, None]
        self.tunnel = [None for i in range(4)]

        for x in range(4):
              #Load a copy of the tunnel
              self.tunnel[x] = loader.loadModelCopy('demo_tunnel/models/tunnel')
              #The front segment needs to be attached to render
              if x == 0: self.tunnel[x].reparentTo(render)
              #The rest of the segments parent to the previous one, so that by moving
              #the front segement, the entire tunnel is moved
              else:      self.tunnel[x].reparentTo(self.tunnel[x-1])
              #We have to offset each segment by its length so that they stack onto
              #each other. Otherwise, they would all occupy the same space.
              self.tunnel[x].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)
              #Now we have a tunnel consisting of 4 repeating segments with a
              #hierarchy like this:
              #render<-tunnel[0]<-tunnel[1]<-tunnel[2]<-tunnel[3]

        #Set up the tunnel to move one segment and then call contTunnel again
        #to make the tunnel move infinitely
        self.tunnelMove = Sequence(
          Func(self.contTunnel),
          LerpFunc(self.mysetZ,
                   duration = TUNNEL_TIME,
                   fromData = 0,
                   toData = TUNNEL_SEGMENT_LENGTH*.305),
          )
        self.tunnelMove.loop()


    def mysetZ(self,t):
        self.tunnel[0].setZ(t)

    def contTunnel(self):
        #This line uses slices to take the front of the list and put it on the
        #back. For more information on slices check the Python manual
        self.tunnel = self.tunnel[1:]+ self.tunnel[0:1]
        #Set the front segment (which was at TUNNEL_SEGMENT_LENGTH) to 0, which
        #is where the previous segment started
        self.tunnel[0].setZ(0)
        #Reparent the front to render to preserve the hierarchy outlined above
        self.tunnel[0].reparentTo(render)
        #Set the scale to be apropriate (since attributes like scale are
        #inherited, the rest of the segments have a scale of 1)
        self.tunnel[0].setScale(.155, .155, .305)
        #Set the new back to the values that the rest of teh segments have
        self.tunnel[3].reparentTo(self.tunnel[2])
        self.tunnel[3].setZ(-TUNNEL_SEGMENT_LENGTH)
        self.tunnel[3].setScale(1)


    def ClearScene(self):
        #self.tunnelMove.pause()
        self.tunnelMove.finish()
        self.att_fog.Destroy()
        base.camera.detachNode()
        #render.clearShaderInput('light')
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def myshader(self):
        myShader = loader.loadShader('shaders/fog.sha')
        render.setShader(myShader)
        render.setShaderInput('alight0', self.att_ambientLight.light)
        render.setShaderInput('fogDensity', self.att_fog.att_expDensity.v, 0, 0, 0)
        render.setShaderInput('fogColor', self.att_fog.att_color.getColor())

    #def Demo2(self):
        #"""Use my fog shader"""
        #self.myshader()


    def usemyfog(self, object):
        if self.att_usemyfog.v:
            self.myshader()
        else:
            render.clearShader()
