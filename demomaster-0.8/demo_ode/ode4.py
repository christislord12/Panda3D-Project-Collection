
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
#from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
#from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdePlaneGeom, OdeTriMeshGeom, OdeTriMeshData
from pandac.PandaModules import BitMask32, Quat, Mat4

# particle
from direct.particles.ParticleEffect import ParticleEffect

import odebase
import demobase, camerabase
import ode1
from shadowManager2 import ShadowManager
####################################################################################################################
class ODEDemo4(ode1.ODEDemo):
    """
    ODE - with Shadow Manager 2
    Enable the ODE demo with Shadow Manager 2
    """
    def __init__(self, parent):
        ode1.ODEDemo.__init__(self, parent)
        self.createEffect = False

    #def LoadModels(self):
        # turn off the auto shader
        #ode1.ODEDemo.LoadModels(self)
        #render.setShaderOff()
        #self.att_shaderoption.setShader(None, False)
        ###render.clearShader()
        ###self.room.setShaderAuto()

    def LoadLights(self):
        ode1.ODEDemo.LoadLights(self)
        self.att_ambinentLight.setColor(None, Vec4(0.17,0.17,0.17,1))
        self.att_directionalLight.setLightOn(None, False)
        self.att_spotLight.setFov(None, 90)
        self.att_spotLight.setExponent(None, 10)
        self.att_spotLight.setPosition(None, Vec3(-13.0,-12.0,20.0))
        self.att_spotLight.setLookAt(None, Vec3(-2.33,12.33,9))
        self.att_spotLight.setColor(None, Vec4(1,1,1,1))

        # Initiate the shadows
        self.att_sMgr = ShadowManager(render, hardness=.55, fov=75)
        if not self.att_sMgr.IsOK():
            demobase.addInstructions(0,-0.5, "Your hardware is not powerful enough to run this demo", align=TextNode.ACenter, node=self.textnode)
        else:
            self.att_sMgr.changeLightPos(Vec3(-15,-24,18),Point3(0.7,0.7,6))
            self.att_sMgr.setStandardControl()

    def ClearScene(self):
        self.att_sMgr.Destroy()
        ode1.ODEDemo.ClearScene(self)
