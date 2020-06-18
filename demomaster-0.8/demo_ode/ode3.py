
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
import demobase, camerabase
import ode1
from shadowManager import ShadowManager
####################################################################################################################
class ODEDemo3(ode1.ODEDemo):
    """
    ODE - with Shadow Manager
    Enable ODE demo with Shadow Manager
    """
    def __init__(self, parent):
        ode1.ODEDemo.__init__(self, parent)
        self.createEffect = False

    def LoadModels(self):
        # turn off the auto shader
        self.att_shaderoption.setShader(None, False)
        ode1.ODEDemo.LoadModels(self)

    def LoadLights(self):
        #self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.35, .35, .35, 1 ))
        #self.att_ambinentLight.setLight(render)

        # Initiate the shadows
        self.att_sMgr = ShadowManager(render, ambient=0.1,hardness=20,fov=60)
        self.att_sMgr.changeLightPos(Vec3(-6,-30,25),Point3(0,20,0))
        self.att_sMgr.setStandardControl()
        #self.parent.Accept("v", base.bufferViewer.toggleEnable)

    def setUntextured(self, np):
        # Otherwise the model will turn up black.
        self.att_sMgr.flagUntexturedObject(np)

    def ClearScene(self):
        self.att_sMgr.Destroy()
        ode1.ODEDemo.ClearScene(self)
