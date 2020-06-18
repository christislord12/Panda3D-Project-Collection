from random import randint, random
import math, os, sys, colorsys, threading, operator, inspect, geomutil


from pandac.PandaModules import Filename,ConfigVariableSearchPath, TransparencyAttrib, ColorBlendAttrib
#Dtool_funcToMethod
from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight
from pandac.PandaModules import TextNode,LightAttrib
from pandac.PandaModules import Vec3,Vec4,Point3
from direct.gui.OnscreenText import OnscreenText
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
from pandac.PandaModules import Material, Fog, Texture
#from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
#from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdePlaneGeom, OdeTriMeshGeom, OdeTriMeshData
from pandac.PandaModules import BitMask32, Quat, Mat4

# particle effect
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import ForceGroup
from pandac.PandaModules import BaseParticleEmitter,BaseParticleRenderer
from pandac.PandaModules import PointParticleFactory,SpriteParticleRenderer
from pandac.PandaModules import LinearNoiseForce,DiscEmitter

# shader
from pandac.PandaModules import ShaderGenerator, Shader

############################################
# to record which nodepath the light is shining on
# only track the object created by Att_Light*
##LIGHTS = {}
##def newsetLight(np, lnp, pri=0):
###    print "set light", lnp
##    np.origsetLight(lnp, pri)
##    if lnp in LIGHTS:
##        LIGHTS[lnp].add((np, pri))
###        print "set light ok"
###    else:
###       LIGHTS[lnp]=set([np])
##
##def newclearLight(np, lnp):
##    np.origclearLight(lnp)
##    if lnp in LIGHTS:
##       LIGHTS[lnp].remove(np)
##
##NodePath.DtoolClassDict["origsetLight"]=NodePath.setLight
##Dtool_funcToMethod(newsetLight,NodePath,"setLight")
##NodePath.DtoolClassDict["origclearLight"]=NodePath.clearLight
##Dtool_funcToMethod(newsetLight,NodePath,"clearLight")

##########################################
def addInstructions(x,y, msg, align=TextNode.ALeft, node=None):
    if node == None:
        #node = render2d
        node = aspect2d
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
			pos=(x, y), align=align, scale = .05, parent=node)

#def addTitle(text):
#    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
#              pos=(1.3,-0.95), align=TextNode.ARight, scale = .07, parent=render2d)

def addInstructionList(x,y,space,msg,align=TextNode.ALeft, node=None):
    msgs = msg.split("\n")
    for msg in msgs:
        addInstructions(x,y,msg,align,node)
        y -= space

use_loader = False
def loadShader(shaderFile):
    if use_loader:
        return loader.loadShader(shaderFile)
    else:
        config = ConfigVariableSearchPath('shader-path')
        n = config.getNumDirectories()
        #file = shaderFile.toOsSpecific()
        for i in range(n):
            dir = config.getDirectory(i).toOsSpecific()
            if dir[-1] != os.sep:
                dir += os.sep
            file = dir + shaderFile
            #print file
            fn = Filename.fromOsSpecific(file)
            fn.makeTrueCase()
            #print fn
            #fn = Filename(file)
            if fn.exists():
                return Shader.load(fn)
        return None


##########################################
class DemoBase():
    def __init__(self, parent):
        self.parent = parent
        # check if the class has defined self.Demoxxx
        # the class instance should also define self.classname
        # each entry function shall accept a parameter
        # def Demo1(fGetName):
        # if fGetName is true, it should result a descriptive name of the function
        self.entries = []
        members = inspect.getmembers(self)
        entries2 = []
        entries1 = []
        for pair in members:
            name,func = pair

            #print name
            if (name.find("Demo") == 0 or name.find("_base") == 0) and inspect.isroutine(func):
                doc = eval("self.%s.__doc__" % name)
                if len(doc) == 0:
                    doc = name
                if name.find("_base") == 0:
                    entries1.append((name,func,doc))
                elif not hasattr(self, "functionlist") or name in self.functionlist:
                    entries2.append((name,func,doc))

        entries1.sort(cmp=lambda x,y: cmp(x[0], y[0]))
        entries2.sort(cmp=lambda x,y: cmp(x[0], y[0]))
        self.entries = entries1 + entries2

        self.wiredmode = False

    def SetCameraPosHpr(self, x, y, z, h, p, r):
        base.camera.setPosHpr(x, y, z, h, p, r)
        self.cameraset()

    def SetCameraPos(self, pos, lookat):
        base.camera.setPos(pos[0], pos[1], pos[2])
        base.camera.lookAt(lookat[0], lookat[1], lookat[2])
        self.cameraset()


    def cameraset(self):
        mat=Mat4(camera.getMat())
        mat.invertInPlace()
        base.mouseInterfaceNode.setMat(mat)
        base.enableMouse()

    def LoadSkyBox(self, skyboxfile, scale=(2000,2000,1000), parent=None):
        skybox = loader.loadModel(skyboxfile)
        # make big enough to cover whole terrain, else there'll be problems with the water reflections
        skybox.setScale(scale[0],scale[1],scale[2])
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        if parent == None:
            parent = render
        skybox.reparentTo(parent)
        return skybox

    def DestroyAllLights(self):
        members = inspect.getmembers(self)
        for pair in members:
            name,value = pair
            if name.find("att_") == 0:
                #if value.__class__  in  [ Att_ambientLightNode,Att_directionalLightNode,Att_pointLightNode,Att_spotLightNode ]:
                if issubclass(value.__class__, Att_lightNode):
                    value.Destroy()

    # basic functions for all demos
    def _base01(self):
        """Information"""
        title,info = self.parent.getDemoInformation(self.__class__)
        self.parent.MessageBox(title, info)

    def _base02(self):
        """Scene Graph"""
        self.parent.ShowSceneGraph()

    def _base03(self):
        """Edit Source"""
        self.parent.ShowDemoSource()

    def _base04(self):
        """Set Wired Mode"""
        render.setRenderModeWireframe()

    def _base05(self):
        """Set Filled Mode"""
        render.setRenderModeFilled()

    def _base06(self):
        """Toggle Buffer Viewer"""
        base.bufferViewer.toggleEnable()

    # very slow, better not use.
    #def _base07(self):
    #    """Capture Movie, 30 seconds"""
    #    base.movie(namePrefix = 'tmp/movie', duration = 30.0, fps = 10,
    #          format = 'png', sd = 4, source = None)

##    def ShowShaderSource(self, node):
##        sg = ShaderGenerator.getDefault()
##        shader = sg.synthesizeShader(node.getState()).getShader()
##        text=shader.getText()
##        self.parent.ShowSource(text=text,nosave=True)


class Att_base():
    def __init__(self, fReadOnly, name=None, NodeName=None):
        self.fReadOnly = fReadOnly
        if name == None:
            name = "Value"
        self.name = name
        self.NodeName = NodeName

    def getNodeName(self):
        if self.NodeName == None:
            return self.name
        return self.NodeName

    def setNotifier(self, notifier):
        self.notifier = notifier

    def notify(self):
        if hasattr(self,'notifier') and inspect.isroutine(self.notifier):
            self.notifier(self)

class Att_Boolean(Att_base):
    def __init__(self, fReadOnly, name, v, NodeName=None):
        Att_base.__init__(self, fReadOnly, name, NodeName)
        self.v = v

    def update(self, v):
        if self.fReadOnly:
            return
        self.v = v

#        if hasattr(self,'notifier') and inspect.isroutine(self.notifier):
#            self.notifier(self)
        self.notify()


class Att_NumRange(Att_base):
    def __init__(self, fReadOnly, name, fInteger, minv, maxv, default, NodeName):
        Att_base.__init__(self, fReadOnly, name, NodeName)
        self.fInteger = fInteger
        self.minv = minv
        self.maxv = maxv
        self.v = default
        self.default = default

    def fix(self):
        if self.minv != self.maxv:
            self.v = max(self.v, self.minv)
            self.v = min(self.v, self.maxv)

    def update(self, v):
        if self.fReadOnly:
            return
        if self.fInteger:
            v = int(v)
        else:
            v = float(v)
        if self.minv >= self.maxv or (v <= self.maxv and v >= self.minv):
            self.v = v

#        if hasattr(self,'notifier') and inspect.isroutine(self.notifier):
#            self.notifier(self)
        self.notify()

class Att_IntRange(Att_NumRange):
    def __init__(self, fReadOnly, name, minv, maxv, default, NodeName=None):
        Att_NumRange.__init__(self,fReadOnly, name, True, minv, maxv, default,NodeName=NodeName)

class Att_FloatRange(Att_NumRange):
    def __init__(self, fReadOnly, name, minv, maxv, default, precision=2,NodeName=None):
        Att_NumRange.__init__(self,fReadOnly, name, False, minv, maxv, default,NodeName=NodeName)
        self.precision = precision


class Att_Vecs(Att_base):
    def __init__(self, fReadOnly, name, l, vec, minv, maxv, precision=2, NodeName=None):
        Att_base.__init__(self, fReadOnly, name, NodeName=NodeName)
        self.l = l
        self.minv = minv
        self.maxv = maxv
        self.fInteger = False
        self.precision = precision
        self.vec = []
        self.default = []
        for i in range(l):
            v = Att_FloatRange(fReadOnly, "%d" % (i+1), minv, maxv, vec[i], precision)
            v.setNotifier(self.update)
            self.vec.append(v)
            self.default.append(vec[i])

    def fix(self):
        for i in range(self.l):
            self.vec[i].fix()

    def setValue(self, v):
        if isinstance(v, Att_Vecs):
            for i in range(self.l):
                self.vec[i].v = v.vec[i].v
        else:
            for i in range(self.l):
                self.vec[i].v = v[i]
        self.fix()

    def update(self, object):
#        if hasattr(self,'notifier') and inspect.isroutine(self.notifier):
#            self.notifier(self)
        self.notify()

    def getListValue(self):
        return self.getValue(True)

    def getValue(self, forcevector=False):
        if not forcevector:
            if self.l == 3:
                return Vec3(self.vec[0].v,self.vec[1].v,self.vec[2].v)
            elif self.l == 4:
                return Vec4(self.vec[0].v,self.vec[1].v,self.vec[2].v,self.vec[3].v)

        ret = []
        for i in range(self.l):
            ret.append(self.vec[i].v)
        return ret


def Color2RGB(c):
    return (int(c[0] * 255),int(c[1] * 255),int(c[2] * 255))
def RGB2Color(rgb,alpha=1):
    return Vec4(float(float(rgb[0]) / 255.0),float(rgb[1] / 255.0),float(rgb[2] / 255.0),alpha)

class Att_color(Att_base):
    def __init__(self, fReadOnly, name, color):
        if name == None:
            name = "Color"
        Att_base.__init__(self, fReadOnly, name)
        self.color = color

    def getRGBColor(self):
        return Color2RGB(self.color)

    def getColor(self):
        return self.color

    def setRGBColor(self,rgb):
        if self.fReadOnly:
            return
        self.color = RGB2Color(rgb)
        self.notify()

    def setColor(self,c):
        if self.fReadOnly:
            return
        self.color = c
        self.notify()

class Att_lightNode(Att_base):
    def __init__(self, fReadOnly, name, color, node):
        Att_base.__init__(self, fReadOnly, name)

        self.att_fOn = Att_Boolean(fReadOnly, "Light On", True)
        self.att_fOn.setNotifier(self.setLightOn)

        self.att_lightcolor = Att_color(fReadOnly, None, color)
        self.att_lightcolor.setNotifier(self.setColor)

        self.node = node
        self.nodepathset = set()
        self.prioritymap = {}
        self.fEnable = True

    def setLight(self, nodepath, pri=0):
        if not self.fEnable:
            return
        self.nodepathset.add(nodepath)
        self.prioritymap[nodepath]=pri
        nodepath.setLight(self.light,pri)

    def clearLight(self, nodepath):
        if not self.fEnable:
            return
        self.nodepathset.remove(nodepath)
        del self.prioritymap[nodepath]
        nodepath.clearLight(self.light)

    def clearAll(self):
        if not self.fEnable:
            return
        for np in self.nodepathset:
            np.clearLight(self.light)
        self.nodepathset.clear()
        self.prioritymap = {}

    def Destroy(self):
        if not self.fEnable:
            return
        self.clearAll()
        self.fEnable = False
        self.light.removeNode()

    def setLightOn(self,object=None,v=None):
        if not self.fEnable:
            return
##        if self.att_fOn.v:
##            self.light.node().setColor(self.att_lightcolor.getColor())
###            render.setLight(self.light)
##        else:
##            self.light.node().setColor(Vec4(0,0,0,1))
###            render.clearLight(self.light)

##            if self.att_fOn.v:
##                render.setLight(self.light)
##            else:
##                render.clearLight(self.light)
        if v != None:
            self.att_fOn.v = v

##        lightnodeset = LIGHTS[self.light]
##        if self.att_fOn.v:
##            for node in lightnodeset:
##                np,pri = node
##                np.origsetLight(self.light, pri)
##        else:
##            for node in lightnodeset:
##                np,pri = node
##                np.origclearLight(self.light)
        for np in self.nodepathset:
            pri = self.prioritymap[np]
            if self.att_fOn.v:
                np.setLight(self.light, pri)
            else:
                np.clearLight(self.light)

        if v == None:
            self.notify()


    def setColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_lightcolor.color = color
        self.light.node().setColor(self.att_lightcolor.getColor())
        if color == None:
            self.notify()

class Att_pointLightNodeBase(Att_lightNode):
    def __init__(self, fReadOnly, name, color, node, attenuation, pos):
        Att_lightNode.__init__(self, fReadOnly, name, color, node)

        self.att_attenuation = Att_Vecs(fReadOnly, "Attenuation", 3, attenuation, 0, 2, 3)
        self.att_attenuation.setNotifier(self.setAttenuation)

        self.att_position = Att_Vecs(fReadOnly, "Position", 3, pos, -100, 100)
        self.att_position.setNotifier(self.setPosition)


    def setAttenuation(self,object=None,v=None):
        if self.fReadOnly:
            return
        if v != None:
            self.att_attenuation.setValue(v)
        attenuation = self.att_attenuation.getValue()
        self.light.node().setAttenuation(attenuation)
        if v == None:
            self.notify()

    def setPosition(self, object=None, v=None):
        if self.fReadOnly:
            return
        if v != None:
            self.att_position.setValue(v)
        position = self.att_position.getValue()
        self.light.setPos(position)
        if v == None:
            self.notify()


class Att_ambientLightNode(Att_lightNode):
    def __init__(self, fReadOnly, name, color, node=None):
        if node == None:
            node = render
        Att_lightNode.__init__(self, fReadOnly, name, color, node)
        self.light = node.attachNewNode( AmbientLight( "ambientLight" ) )
        self.light.node().setColor( color )
        #self.registerLight()
        #render.setLight( self.light )


class Att_directionalLightNode(Att_lightNode):
    def __init__(self, fReadOnly, name, color, direction, node=None):
        if node == None:
            node = render
        Att_lightNode.__init__(self, fReadOnly, name, color, node)
        self.light = node.attachNewNode( DirectionalLight( name ) )
        self.light.node().setColor( color )
        self.light.node().setDirection(direction)
        #self.registerLight()
        #render.setLight( self.light )

        self.att_direction = Att_Vecs(fReadOnly, "Direction", 3, direction, -100, 100)
        self.att_direction.setNotifier(self.setDirection)

    def setDirection(self, object=None,v=None):
        if self.fReadOnly:
            return
        if v != None:
            self.att_direction.setValue(v)
        direction = self.att_direction.getValue()
        self.light.node().setDirection(direction)
        if v == None:
            self.notify()

class Att_pointLightNode(Att_pointLightNodeBase):
    def __init__(self, fReadOnly, name, color, pos, attenuation=(0,0,0), fBulb=False, node=None):
        if node == None:
            node = render
        Att_pointLightNodeBase.__init__(self, fReadOnly, name, color, node, attenuation, pos)
        self.light = node.attachNewNode( PointLight( name ) )
        self.light.node().setColor( color )
        self.light.node().setAttenuation(attenuation)
        self.light.setPos(pos)
        #self.registerLight()

        if fBulb:
#            if color == Vec4(1,1,1,1):
            self.att_bulb = Att_bulb2(fReadOnly, "Bulb", self.light)
#            else:
#                self.att_bulb = Att_bulb(fReadOnly, "Bulb", self.light, color, color)
            self.att_bulb.setBulbState(self.att_fOn.v)

        self.fBulb = fBulb
        self.att_fOn.setNotifier(self.setLightOn)

    def setLightOn(self, object=None, v=None):
        Att_lightNode.setLightOn(self, object, v)
        if self.fBulb:
            self.att_bulb.setBulbState(self.att_fOn.v)

    def Destroy(self):
        if not self.fEnable:
            return
        if self.fBulb:
            self.att_bulb.Destroy()
        Att_lightNode.Destroy(self)

class Att_spotLightNode(Att_pointLightNodeBase):
    def __init__(self, fReadOnly, name, color, fov, exponent, pos, lookAt, attenuation=(0,0,0), node=None):
        if node == None:
            node = render
        Att_pointLightNodeBase.__init__(self, fReadOnly, name, color, node, attenuation, pos)
        self.light = node.attachNewNode( Spotlight( name ) )
        self.light.node().setColor( color )
        self.light.node().setLens( PerspectiveLens() )
        self.light.node().getLens().setFov( fov, fov )
        self.light.node().setExponent(exponent)
        self.light.node().setAttenuation(attenuation)
        self.light.setPos(pos)
        self.light.lookAt(lookAt)

        #self.registerLight()
        #render.setLight( self.light )

        self.att_fov = Att_FloatRange(False, "Fov", 0, 90, fov)
        self.att_fov.setNotifier(self.setFov)
        self.att_exponent = Att_IntRange(False, "Exponent", 0, 128, exponent)
        self.att_exponent.setNotifier(self.setExponent)
        self.att_lookAt = Att_Vecs(fReadOnly, "Look at", 3, lookAt, -20, 20)
        self.att_lookAt.setNotifier(self.setLookAt)

    def setLookAt(self, object=None,v=None):
        if self.fReadOnly:
            return
        if v != None:
            self.att_lookAt.setValue(v)
        lookAt = self.att_lookAt.getValue()
        self.light.lookAt(Point3(lookAt[0],lookAt[1],lookAt[2]))
        if v == None:
            self.notify()

    def setExponent(self, object=None,v=None):
        if self.fReadOnly:
            return
        if v != None:
            self.att_exponent.v = v
        exponent = self.att_exponent.v
        self.light.node().setExponent(exponent)
        if v == None:
            self.notify()

    def setFov(self,object=None,v=None):
        if self.fReadOnly:
            return
        if v != None:
            self.att_fov.v = v
        fov = self.att_fov.v
        self.light.node().getLens().setFov(fov,fov)
        if v == None:
            self.notify()

####################################################################################################

class Att_AutoShaderOption(Att_base):
    def __init__(self, fReadOnly, name, v):
        Att_base.__init__(self, fReadOnly, name)
        self.att_fOption = Att_Boolean(fReadOnly, name, v)
        self.att_fOption.setNotifier(self.setShader)
        self.setShader()

    def setShader(self, object=None, v=None):
        if v != None:
            self.att_fOption.v = v
        if self.att_fOption.v:
            render.setShaderAuto()
        else:
            #render.setShaderOff()
            render.clearShader()
        if v == None:
            self.notify()

# a simulated bulb
class Att_bulb(Att_base):
    def __init__(self, fReadOnly, name, node, bulbColor=Vec4(1,1,1,1), fireColor=Vec4(0.64,0.9,0.9,1), bulbsize=1, fireScale=5):
        Att_base.__init__(self, fReadOnly, name)

        if node == None:
            node = render
        self.node = node

        self.att_fOn = Att_Boolean(fReadOnly, "Bulb On", True)
        self.att_fOn.setNotifier(self.setBulbOn)

        self.att_bulbColor = Att_color(fReadOnly, "Bulb", bulbColor)
        self.att_bulbColor.setNotifier(self.setBulbColor)

        self.att_fireColor = Att_color(fReadOnly, "Fire Color", fireColor)
        self.att_fireColor.setNotifier(self.setFireColor)

        self.att_bulbSize = Att_FloatRange(fReadOnly, "Bulb Size", 0.1, 20, bulbsize)
        self.att_bulbSize.setNotifier(self.setBulbSize)

        self.att_fireScale = Att_FloatRange(fReadOnly, "Fire Size", 1, 20, fireScale)
        self.att_fireScale.setNotifier(self.setFireScale)

        self.sphere = loader.loadModel("models/ball")
        self.sphere.reparentTo(node)
        self.sphere.setScale(bulbsize)

##            lAttrib = LightAttrib.makeAllOff()
##            self.bLight = AmbientLight( "bulblight" )
##            self.bLight.setColor( bulbColor)
##            lAttrib = lAttrib.addLight( self.bLight )
##            self.sphere.attachNewNode( self.bLight )
##            self.sphere.node().setAttrib( lAttrib )


        self.bLight = AmbientLight( "bulblight" )
        self.bLight.setColor( bulbColor)
        self.bLightNode = node.attachNewNode( self.bLight )
        self.sphere.setLightOff()
        self.sphere.setLight(self.bLightNode)

        self.dummyNode = node.attachNewNode("particleNode")
        self.pLight = AmbientLight( "particlelight" )
        self.pLight.setColor( fireColor)
        self.pLightNode = node.attachNewNode( self.pLight)
        self.dummyNode.setLightOff()
        self.dummyNode.setLight(self.pLightNode)

        self.particle = ParticleEffect()
        self.particle.loadConfig(Filename("share/particles/whitelight.ptf"))
        #self.particle.loadConfig(Filename("particles/steam.ptf"))
        psize = self.att_fireScale.v * bulbsize
        self.particle.setScale(psize)
        self.particle.start(self.dummyNode)
        self.fBulbState=True
        self.fEnable = True

    def setBulbColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_bulbColor.color = color
        self.bLight.setColor(self.att_bulbColor.getColor())
        if color == None:
            self.notify()

    def setBulbState(self, v):
        self.fBulbState = v
        self.setBulbOn()

    def setBulbOn(self, object=None, v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_fOn.v = v
        if self.att_fOn.v and self.fBulbState:
            self.particle.enable()
            self.particle.start(self.dummyNode)
            #self.particle.reset()
            self.sphere.show()
            self.dummyNode.show()
        else:
            self.particle.disable()
            self.sphere.hide()
            self.dummyNode.hide()
        if v == None:
            self.notify()

    def setFireColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_fireColor.color = color
        self.pLight.setColor(self.att_fireColor.getColor())
        if color == None:
            self.notify()


    def setFireScale(self, object=None, v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_fireScale.v = v
        self.changesize()
        if v == None:
            self.notify()

    def setBulbSize(self, object=None, v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_bulbSize.v = v

        self.changesize()
        if v == None:
            self.notify()

    def changesize(self):
        bulbsize = self.att_bulbSize.v
        self.sphere.setScale(bulbsize)
        psize = self.att_fireScale.v * bulbsize
        self.particle.setScale(psize)

    def Destroy(self):
        if not self.fEnable:
            return
        self.fEnable = False
        self.particle.disable()
        self.particle.cleanup()
        self.sphere.clearLight(self.bLightNode)
        self.dummyNode.clearLight(self.pLightNode)
        self.sphere.removeNode()
        self.pLightNode.removeNode()
        self.bLightNode.removeNode()
        self.dummyNode.removeNode()


# a simulated bulb, this one use a Billboard and texture
class Att_bulb2(Att_base):
    def __init__(self, fReadOnly, name, node, bulbColor=Vec4(1,1,1,1), fireColor=Vec4(0.64,0.9,0.9,1), bulbsize=1, fireScale=1.5):
        Att_base.__init__(self, fReadOnly, name)

        if node == None:
            node = render
        self.node = node

        self.att_fOn = Att_Boolean(fReadOnly, "Bulb On", True)
        self.att_fOn.setNotifier(self.setBulbOn)

        self.att_bulbColor = Att_color(fReadOnly, "Bulb", bulbColor)
        self.att_bulbColor.setNotifier(self.setBulbColor)

        self.att_fireColor = Att_color(fReadOnly, "Fire Color", fireColor)
        self.att_fireColor.setNotifier(self.setFireColor)

        self.att_bulbSize = Att_FloatRange(fReadOnly, "Bulb Size", 0.1, 20, bulbsize)
        self.att_bulbSize.setNotifier(self.setBulbSize)

        self.att_fireScale = Att_FloatRange(fReadOnly, "Fire Size", 1, 20, fireScale)
        self.att_fireScale.setNotifier(self.setFireScale)

        self.bulb = self.createBillboard(node, 4, 4, "textures/dot.png")
        self.bulb.setScale(bulbsize)
        self.bulb.setColor(bulbColor)

        self.fire = self.createBillboard(node, 4, 4, "textures/flare1.png")
        self.fire.setScale(bulbsize)
        self.fire.setColor(fireColor)

        self.fBulbState=True
        self.fEnable = True

    def createBillboard(self, parent, nx, ny, file):
        np = geomutil.createPlane('myplane',nx,ny,1,1)
        np.setHpr(0,90,0)
        np.reparentTo(parent)
        #self.bulb.setScale(bulbsize)
        np.setBillboardPointWorld()
        np.setDepthWrite( False )
        np.setTransparency( TransparencyAttrib.MAlpha )
        attrib = ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
        np.node().setAttrib(attrib)
        np.setBin('fixed', 0)
        tex = loader.loadTexture(file)
        tex.setMinfilter( Texture.FTLinearMipmapLinear )
        tex.setMagfilter( Texture.FTLinearMipmapLinear )
        tex.setAnisotropicDegree(2)
        np.setTexture(tex)
        np.setLightOff()
        return np

    def setBulbColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_bulbColor.color = color
        self.bulb.setColor(self.att_bulbColor.getColor())
        if color == None:
            self.notify()

    def setBulbState(self, v):
        self.fBulbState = v
        self.setBulbOn()

    def setBulbOn(self, object=None, v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_fOn.v = v
        if self.att_fOn.v and self.fBulbState:
            self.bulb.show()
            self.fire.show()
        else:
            self.bulb.hide()
            self.fire.hide()
        if v == None:
            self.notify()

    def setFireColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_fireColor.color = color
        self.fire.setColor(color)
        if color == None:
            self.notify()


    def setFireScale(self, object=None, v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_fireScale.v = v
        self.changesize()
        if v == None:
            self.notify()

    def setBulbSize(self, object=None, v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_bulbSize.v = v

        self.changesize()
        if v == None:
            self.notify()

    def changesize(self):
        bulbsize = self.att_bulbSize.v
        self.bulb.setScale(bulbsize)
        psize = self.att_fireScale.v * bulbsize
        self.fire.setScale(psize)

    def Destroy(self):
        if not self.fEnable:
            return
        self.fEnable = False
        self.bulb.removeNode()
        self.fire.removeNode()


########################################################

class Att_backgroundColor(Att_base):
    def __init__(self, fReadOnly, name, color):
        Att_base.__init__(self, fReadOnly, name)

        self.att_color = Att_color(fReadOnly, None, color)
        self.att_color.setNotifier(self.setColor)

        self.setColor()

    def setColor(self, object=None, color=None):
        if color != None:
            self.att_color.color = color
        base.setBackgroundColor(self.att_color.color[0],self.att_color.color[1],self.att_color.color[2])

        if color == None:
            self.notify()

class Att_exponentialFog(Att_base):
    def __init__(self, fReadOnly, name, color, expDensity):
        Att_base.__init__(self, fReadOnly, name)

        self.att_fOn = Att_Boolean(fReadOnly, "Fog On", True)
        self.att_fOn.setNotifier(self.setFogOn)

        self.att_color = Att_color(fReadOnly, None, color)
        self.att_color.setNotifier(self.setColor)

        self.att_expDensity = Att_FloatRange(fReadOnly,"Exp Density", 0.0,1,expDensity,3)
        self.att_expDensity.setNotifier(self.setExpDensity)

        self.nodepathset = set()
        self.fEnable = True

        self.expFog = Fog(name)
        self.setColor()
        self.setExpDensity()


    def setFogOn(self,object=None,v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_fOn.v = v
        for np in self.nodepathset:
            if self.att_fOn.v:
                np.setFog(self.expFog)
            else:
                np.clearFog()
        if v == None:
            self.notify()

    def setColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_color.color = color
        self.expFog.setColor(self.att_color.color[0],self.att_color.color[1],self.att_color.color[2])
        if color == None:
            self.notify()

    def setExpDensity(self, object=None, density=None):
        if not self.fEnable:
            return
        if density != None:
            self.att_expDensity.v = density
        self.expFog.setExpDensity(self.att_expDensity.v)
        if density == None:
            self.notify()

    def setFog(self, node):
        if not self.fEnable:
            return
        self.nodepathset.add(node)
        node.setFog(self.expFog)

    def clearFog(self,node):
        if not self.fEnable:
            return
        self.nodepathset.remove(node)
        node.clearFog()


    def clearAll(self):
        if not self.fEnable:
            return
        for np in self.nodepathset:
            np.clearFog()
        self.nodepathset.clear()


    def Destroy(self):
        if not self.fEnable:
            return
        self.clearAll()
        self.fEnable = False


class Att_linearFog(Att_base):
    def __init__(self, fReadOnly, name, color, linrange, fallback_angle, fallback_onset, fallback_opaque):
        Att_base.__init__(self, fReadOnly, name)

        self.att_fOn = Att_Boolean(fReadOnly, "Fog On", True)
        self.att_fOn.setNotifier(self.setFogOn)

        self.att_color = Att_color(fReadOnly, None, color)
        self.att_color.setNotifier(self.setColor)

        self.att_range = Att_Vecs(False,"Range",2,linrange,0,500)
        self.att_range.setNotifier(self.setRange)

        self.att_angle = Att_FloatRange(fReadOnly,"FB angle", -90,90,fallback_angle,2)
        self.att_angle.setNotifier(self.setFallback)
        self.att_onset = Att_FloatRange(fReadOnly,"FB onset", 0,1000,fallback_onset,0)
        self.att_onset.setNotifier(self.setFallback)
        self.att_opaque = Att_FloatRange(fReadOnly,"FB opaque", 0,1000,fallback_opaque,0)
        self.att_opaque.setNotifier(self.setFallback)

        self.nodepathset = set()
        self.fEnable = True

        self.linFog = Fog(name)
        self.setColor()
        self.setRange()


    def setFogOn(self,object=None,v=None):
        if not self.fEnable:
            return
        if v != None:
            self.att_fOn.v = v
        for np in self.nodepathset:
            if self.att_fOn.v:
                np.setFog(self.linFog)
            else:
                np.clearFog()
        if v == None:
            self.notify()

    def setColor(self, object=None, color=None):
        if not self.fEnable:
            return
        if color != None:
            self.att_color.color = color
        self.linFog.setColor(self.att_color.color[0],self.att_color.color[1],self.att_color.color[2])
        if color == None:
            self.notify()

    def setRange(self,object=None,range=None):
        if not self.fEnable:
            return
        if range != None:
            self.att_range.setValue(range)
        self.linFog.setLinearRange(* self.att_range.getListValue())

    def setFallback(self, object=None, angle=None, onset=None, opaque=None):
        if not self.fEnable:
            return
        if angle != None:
            self.att_angle.v = angle
        if onset != None:
            self.att_onset.v = onset
        if opaque != None:
            self.att_opaque.v = opaque

        self.linFog.setLinearFallback(self.att_angle.v, self.att_onset.v, self.att_opaque.v)
        if angle == None and onset==None and opaque==None:
            self.notify()

    def setFog(self, node):
        if not self.fEnable:
            return
        self.nodepathset.add(node)
        node.setFog(self.linFog)

    def clearFog(self,node):
        if not self.fEnable:
            return
        self.nodepathset.remove(node)
        node.clearFog()


    def clearAll(self):
        if not self.fEnable:
            return
        for np in self.nodepathset:
            np.clearFog()
        self.nodepathset.clear()


    def Destroy(self):
        if not self.fEnable:
            return
        self.clearAll()
        self.fEnable = False
