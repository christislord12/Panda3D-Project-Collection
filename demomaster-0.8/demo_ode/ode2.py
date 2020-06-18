
from random import randint, random
import math, sys, colorsys, threading

#import direct.directbase.DirectStart
from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
from pandac.PandaModules import Material,LightAttrib

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3

# ode
from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdePlaneGeom, OdeTriMeshGeom, OdeTriMeshData
from pandac.PandaModules import BitMask32, Quat, Mat4

# particle
from direct.particles.ParticleEffect import ParticleEffect

import odebase
import demobase
import ode1
#import shadowmanager
####################################################################################################################
class ODEDemo2(ode1.ODEDemo):
    """
    ODE - Demo 2
    Test subclassing.
    """
    def __init__(self, parent):
        ode1.ODEDemo.__init__(self, parent)


    def LoadModels(self):
        #render.setShaderOff() # turn off the auto shader by default
        #self.att_shaderoption.setShader(None, False)
        #self.smgr = shadowmanager.ShadowManager()
        #self.parent.Accept("v", base.bufferViewer.toggleEnable)

        room = loader.loadModel("demo_normalmap/models/abstractroom")
        room.reparentTo(render)
        room.setScale(0.333,0.333,0.4)
        #room.setPos(-20,20,0)
        #room.setPos(0,-10,0)
        room.setPos(0,-10,-0.1)
        room.flattenLight()

        box = loader.loadModel("models/box")
        odebase.MakeRoom(render,box,self.odeworld, 1,1,
            [-20.0,-20.0,0.0], [20.0,20.0,20.0], 5.0, 5)

        self.odeworld.AddObject(odebase.ODEtrimesh(self.odeworld,self.odeworld.space,room, None, 0, 0, 1, 1))
        self.room = room
        self.roomheight = 20
        #self.SetCameraPos(Vec3(0,-60,10), Vec3(0,0,10))
        self.defaultpos = Vec3(0,-60,self.roomheight/2)
