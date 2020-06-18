
from random import randint, random
import math, sys, colorsys, threading
import odebase
import demobase, camerabase, skydome2

from pandac.PandaModules import Filename
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec2,Vec3,Vec4,Point3,Texture,TextureStage,VBase3, Quat, TransparencyAttrib, Material
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import OdeHinge2Joint
from direct.interval.IntervalGlobal import *

# particle
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

debugCamera = False
useShadowManager = 0

if useShadowManager == 1:
   from shadowManager import ShadowManager
elif useShadowManager == 2:
   from shadowManager2 import ShadowManager
elif useShadowManager == 3:
    import PSSM.ParallelSplitShadowMap

####################################################################################################################
class ODECar1Demo(demobase.DemoBase):
    """
    ODE Car - Demo 1
    From ninth @ http://www.panda3d.org/phpbb2/viewtopic.php?t=5646
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.textnode = render2d.attachNewNode("textnode")
        self.numnode =  demobase.addInstructions(0.8,0.9,"",TextNode.ARight, self.textnode)
        self.odeworld = odebase.ODEWorld_Simple()

        #self.odeworld = self.parent.odeworld
        #self.odeworld.setNotifier(self)


        #if useShadowManager==0:
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.LoadModels()
        self.LoadSkyBox()
        taskMgr.add(self.timeUpdated, "timeUpdated")
        self.LoadLights()


        if debugCamera:
            self.SetupCamera()
            self.setupKeyboard()
            self.tasks = Sequence(
                Func(self.car.brake),
                Func(self.car.startEngine),
                Wait(1),
                Func(self.DropBoxes))
        else:
            self.demonote = self.textnode.attachNewNode("textnode")
            demobase.addInstructionList(0,-0.85,0.05,
"""Use Arrow key to drive.
Press SPACE and SHIFT keys to brake.
V key to toggle Camera view.
""", align=TextNode.ACenter, node=self.demonote)

            self.SetCameraPosHpr(-12,39,10,-150,-10,0)
            self.tasks = Sequence(
                Func(self.car.brake),
                Func(self.car.startEngine),
                Wait(0.7),
                Func(self.car.changeHeadLights, True),
                Wait(0.3),
                Func(self.car.changeHeadLights, False),
                Wait(0.3),
                Func(self.car.changeHeadLights, True),
                Wait(0.3),
                Func(self.car.changeHeadLights, False),
                Wait(0.3),
                Func(self.car.changeHeadLights, True),
                Wait(1.5),
                Func(self.car.setSyncCamera, True),
                Wait(3),
                Func(self.car.releasebrake),
                Func(self.DropBoxes),
                Func(self.demonote.removeNode),
                Wait(1),
                Func(self.setupKeyboard)
                )
        self.tasks.start()

        base.disableMouse()
        self.setupShadowManager()

        self.odeworld.EnableODETask(3)

        self.colorindex = 1
        self.colors = [ Vec4(0,0.8,0,1), Vec4(0,0,0.6,1), Vec4(0.6,0.6,0,1), Vec4(0.7,0,0,1)]
        self.Demo05()

    def SetupCamera(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-100,-100,0], [100,100,100],
                     [-45,45, -10],
                     [0,0,-150],
                     #Vec3(0,-33,13.5),
                    Vec3(-11.7,39,10),
                     rate=0.3, speed=20, distance=5)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.ShowPosition(self.textnode)

    def ClearScene(self):
        if useShadowManager > 0:
            self.att_sMgr.Destroy()
            taskMgr.remove("updateShadowManager")

        self.tasks.finish()

        if hasattr(self, "att_skydome"):
            self.att_skydome.Destroy()
        taskMgr.remove("timeUpdated")
        #self.odeworld.removeNotifier(self)
        if self.car != None:
            self.car.Destroy()
            self.car = None

        self.odeworld.EnableODETask(0)
        if debugCamera:
            self.att_cameracontrol.Destroy()

        self.textnode.removeNode()
        #self.ClearObjects()
        self.odeworld.DestroyAllObjects()
        base.camera.detachNode()

        # remove all lights
        self.DestroyAllLights()

        #render.getChildren().detach()
        render.removeChildren()
        base.camera.reparentTo(render)


    def timeUpdated(self, task):
        self.att_skydome.skybox.setShaderInput('time', task.time)
        return task.cont

    def LoadSkyBox(self):
        #self.att_skydome = skydome1.SkyDome1(render, texturefile='textures/clouds_bw.png')
        self.att_skydome = skydome2.SkyDome2(render)
        self.att_skydome.setStandardControl()
        self.att_skydome.att_skycolor.setColor(Vec4(0.3,0.3,0.3,1))
        self.att_skydome.setPos(Vec3(0,0,-400))


        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def LoadModels(self):
        base.setBackgroundColor(0,0,0)
        world = self.odeworld.world
        space = self.odeworld.space

        world.setGravity(0, 0, -10)

        world.initSurfaceTable(4)
        # surface 1, 2 is the wheels
        # surface 3 is the wall
        # (surfaceId1, surfaceId2, mu, bounce, bounce_vel, soft_erp, soft_cfm, slip, dampen)
        world.setSurfaceEntry(0, 0, 0.8, 0.0, 10, 0.9, 0.00001, 100, 0.002)
        world.setSurfaceEntry(0, 1, 0.8, 0.1, 10, 0.8, 0.00005, 0, 1)
        world.setSurfaceEntry(0, 2, 0.9, 0.1, 10, 0.8, 0.00005, 0, 1)
        world.setSurfaceEntry(3, 1, 0.4, 0.2, 10, 0.7, 0.00005, 0, 1)
        world.setSurfaceEntry(3, 2, 0.4, 0.2, 10, 0.7, 0.00005, 0, 1)

        # the border, surface = 2
        b1 = loader.loadModel('models/border.egg')
        b1.setScale(8,8,6)
        b1.flattenStrong()  #apply transform before read vertex info for create ODE geometry
        b1.reparentTo(render)

        #Our border must collide with the box and car, but never with the road
        border_ode = odebase.ODEtrimesh(world, space, realObj=b1, collObj=None,
                       mass=0, surfaceId=3, collideBits=6, categoryBits=1)
        self.odeworld.AddObject(border_ode)

        # the road similar the border
        road = loader.loadModel('models/track.egg')
        road.setScale(8)
        road.flattenLight()
        road.reparentTo(render)
        #road.getTexture().setMagfilter(Texture.FTLinear)
        road_ode = odebase.ODEtrimesh(world, space, realObj=road, collObj=None,
                       mass=0, surfaceId=0, collideBits=6, categoryBits=1)
        self.odeworld.AddObject(road_ode)

        #notifier = self.odeCollisionEvent
        notifier = None
        self.car = ODECar1(self.odeworld, Vec3(0,15,4), False,
            notifier)

    def odeCollisionEvent(self, odeobject, geomcollided, entry):
        #print "collision"
        pass

    def setupKeyboard(self):
        self.parent.Accept("v", self.car.toggleCameraMode)
        self.parent.Accept("arrow_up", self.car.forward)
        self.parent.Accept("arrow_up-up", self.car.normal)
        self.parent.Accept("arrow_down", self.car.backward)
        self.parent.Accept("arrow_down-up", self.car.normal)
        self.parent.Accept("space", self.car.brake, [200.0])
        self.parent.Accept("space-up", self.car.releasebrake)
        self.parent.Accept("shift", self.car.brake, [70.0])
        self.parent.Accept("shift-up", self.car.releasebrake)
        self.parent.Accept("arrow_left", self.car.Turn, [True,-0.01])
        self.parent.Accept("arrow_left-up", self.car.Turn, [False,-0.01])
        self.parent.Accept("arrow_right", self.car.Turn, [True,0.01])
        self.parent.Accept("arrow_right-up", self.car.Turn, [False,0.01])

    def LoadLights(self):
        # these variable can be controlled by user thru wxUI
        #self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.35, .35, .35, 1 ))
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.6, .6, .6, 1 ))
        self.att_ambientLight.setLight(render)
#        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.4, .4, .4, 1 ),  Vec3( 1, 1, -2 ))
#        self.att_directionalLight.setLight(render)

#        self.att_spotLight = demobase.Att_spotLightNode(False, "Light:Spotlight",  Vec4( .45, .45, .45, 1 ), 88, 28.0, Vec3(0,-20,10), Point3(0,0,10), attenuation=Vec3( 1, 0.0, 0.0 ))
#        self.att_spotLight.setLight(render)

        # this light shine the car
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
            Vec4( 0.4, 0.4, 0.4, 1 ),
            #Vec3(0,0,0),
            Vec3(0,11,4),
            attenuation=Vec3( 0.0, 0.03, 0.0 ),
            #node=base.camera,
            node=self.car.carbody,
            fBulb=False)
        self.att_pointLight.setLight(self.car.carbody_view)

        self.att_pointLight2 = demobase.Att_pointLightNode(False, "Light:Point Light 2",  \
            Vec4( 0.5, 0.5, 0.5, 1 ),
            #Vec4( 0.7, 0.7, 0.7, 1 ),
            Vec3(0,0,0),
            attenuation=Vec3( 0.0, 0.03, 0.0 ),
            node=base.camera,
            fBulb=False)
        self.att_pointLight2.setLight(render)



    def DropBoxes(self):
        """Drop Balls/Boxes"""
        x = loader.loadModel("models/cube")
        x.setScale(3)
        wood = loader.loadTexture("models/wood.png")
        wood.setWrapU(Texture.WMClamp)
        wood.setWrapV(Texture.WMClamp)

        ts = TextureStage("ts")
        ts.setSort(1)
        x.setTexture(ts, wood)

        b = loader.loadModel("models/ball")
        b.setScale(3)
        nops = loader.loadTexture("models/nops.png")
        nops.setWrapU(Texture.WMRepeat)
        nops.setWrapV(Texture.WMRepeat)
        #b.clearTexture()
        b.setTexture(ts, nops)

        y = loader.loadModel("models/cylinder")
        y.setScale(0.5,0.5,3)

        #ball.setTextureOff()
        r = 0.5
        density = 0.015
        nrballs = 20
        catbit = 2
        collidebit = 255
        for i in range(nrballs): #randint(15, 30)):
            # Setup the geometry
            v = randint(0,2)
            if v == 0:
                bNP = x.copyTo(render)
                #bNP.setTexScale(ts,0.5,0.5)
                #bNP.setTexRotate(ts, 45)
            elif v ==2:
                bNP = y.copyTo(render)
            else:
                bNP = b.copyTo(render)
            #bNP.setPos(0, 15, 10)
            bNP.setPos(randint(-30, 30), randint(85, 385), 50)
            bNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45))
            if v == 0:
                b_ode = odebase.ODEbox(self.odeworld.world, self.odeworld.space, bNP, None, density, 0, collidebit, catbit)
            elif v == 1:
                b_ode = odebase.ODEsphere(self.odeworld.world, self.odeworld.space, bNP, None, density, 0, collidebit, catbit)
                b_ode.motionfriction = 0.2
                b_ode.angularfriction = 0.02
            elif v == 2:
                bNP.setColor(random(), random(), random(), 1)
                b_ode = odebase.ODEcylinder(self.odeworld.world, self.odeworld.space, bNP, None, density, 3, 0.5, 3, 0, collidebit, catbit)
                #b_ode = odebase.ODECappedCylinder(self.odeworld.world, self.odeworld.space, bNP, None, density, 3, 1, 1, 0, 0, 0)
            self.odeworld.AddObject(b_ode)


    # this function is created for use a shadowmanager later
    def setUntextured(self, np):
        pass

    def setupShadowManager(self):
        if useShadowManager == 2:
            self.att_sMgr = ShadowManager(render,hardness=.55,fov=60)
            if not self.att_sMgr.IsOK():
                demobase.addInstructions(0,-0.5, "Your hardware is not powerful enough to run this demo", align=TextNode.ACenter, node=self.textnode)
            else:
                self.att_sMgr.changeLightPos(Vec3(5,-16,30),self.human.model.getPos())
                self.att_sMgr.setStandardControl()
        if useShadowManager == 3:
            self.att_sMgr = PSSM.ParallelSplitShadowMap.ParallelSplitShadowMap(
    			Vec3(0, 1, -1),
    			lightsQuality = [2048, 2048, 1024],
    			pssmBias = 0.98,
    			pushBias = 0.3,# pushBias = 0.03,
    			lightColor = VBase3(0.125, 0.149, 0.160),
                #lightColor = VBase3(0.5, 0.5, 0.5),
    			lightIntensity = 0.8)
            self.att_sMgr.setStandardControl()
            taskMgr.add(self.updateShadowManager, "updateShadowManager")

    def updateShadowManager(self, task):
        if useShadowManager == 3:
            self.att_sMgr.update()
        return task.cont

    def Demo05(self):
        """Toggle Color"""
        self.colorindex = (self.colorindex + 1) % len(self.colors)
        c = self.colors[self.colorindex]
        self.car.changeCarColor(c)

    def Demo11(self):
        """Default View"""
        self.car.changeCameraMode(ODECar1.CAMERA_DEFAULT_MODE)

    def Demo12(self):
        """Sticky View"""
        self.car.changeCameraMode(ODECar1.CAMERA_STICKY_MODE)

    def Demo13(self):
        """Driver View"""
        self.car.changeCameraMode(ODECar1.CAMERA_DRIVER_MODE)

class ODECar1():
    CAMERA_DEFAULT_MODE = 0
    CAMERA_STICKY_MODE = 1
    CAMERA_DRIVER_MODE = 2
    modelpath = "models/car1"
    def __init__(self,odeworld,pos,syncCamera=True, odeEventHandler=None):
        self.odeworld = odeworld
        self.syncCamera=syncCamera
        world = odeworld.world
        space = odeworld.space
        #variables
        world.setContactSurfaceLayer(0.01)
        self.cameramode = self.CAMERA_DEFAULT_MODE
        self.turn=False
        self.turnspeed=0.0
        self.turnangle=0.0
        self.carOrientation=1
        self.acceleration=False
        self.maxSpeed=0
        self.accForce=0
        self.stoppingforce = 0
        self.objects = []

        taskMgr.add(self.myTasks, "ode car task")
        #taskMgr.doMethodLater(0.5,self.checkRotation, "checkRotation")

        #Body of the our car - similar the boxes
        if True:
            self.carbody = loader.loadModel("%s/car_box" % self.modelpath)
            bodyHeight=0
            bodyShift = 0
            self.carbody.setPos(pos)
            self.carbody.reparentTo(render)
            density = 4
            collidebit = 3
            catbit = 4
            self.carbody_ode = odebase.ODEbox(world,space,
                self.carbody,
                None, density, 0, collidebit, catbit)
        else:
            self.carbody = loader.loadModel("%s/car_box" % self.modelpath)
            # the collision geom is bigger than the body
            carbody_col = loader.loadModel("models/cube")
            carbody_col.setScale(3.8,5.5,3.5)
            carbody_col.flattenStrong()
            bodyHeight=0
            shift = 1.3
            #bodyShift = -shift
            bodyShift = 0
            carbody_col.setPos(pos[0],pos[1],pos[2]-shift)
            #self.carbody = carbody_col
            self.carbody.setPos(pos[0],pos[1],pos[2]-shift)
            self.carbody.reparentTo(render)
            #self.carbody.hide()

            #density = 0.05468
            density = 0.1
            #density = 4
            collidebit = 3
            catbit = 4
            self.carbody_ode = odebase.ODEbox(world,space,
                self.carbody,
                carbody_col, density, 0, collidebit, catbit)
            M = self.carbody_ode.body.getMass()
            #M2 = OdeMass()
            #M2.set
            #M.add(M2)
            #self.carbody_ode.body.setMass(M)
            self.carbody_ode.geom.setOffsetPosition(0,0,shift*2)
        odeworld.AddObject(self.carbody_ode)
        self.objects.append(self.carbody_ode)

        # car appearance specific
        self.carbody_view = loader.loadModel("%s/car1" % self.modelpath)
        self.carbody_view.setScale(0.8,0.8,0.8)
        #self.carbody_view.setZ(1.2)
        self.carbody_view.setZ(bodyShift)
        self.carbody_view.setTwoSided(True)
        self.carbody_view.reparentTo(self.carbody)
        #self.carbody_view.hide()
        #self.carbody_view.setRenderModeWireframe()
        nodes = [ "head.L", "head.R", "rear.L", "rear.R"]
        self.lights = []
        for node in nodes:
            np = self.carbody_view.find("**/%s" % node)
            np.setLightOff()
            self.lights.append(np)
        self.npTubes = [ self.carbody_view.find("**/tube.L"), self.carbody_view.find("**/tube.R") ]
        self.npBody = self.carbody_view.find("**/body")
        self.lightsTexture1 = loader.loadTexture("%s/car1.png" % self.modelpath)
        self.lightsTexture2 = loader.loadTexture("%s/car2.png" % self.modelpath)
        self.allowTurnover = False
        # car appearance specific ended


        self.joints=[] #suspensions
        self.wheels=[]     #wheels visualisation
        self.wheels_ode = []

        wheelDistance = 2.4 #1.8
        #bodyDistance = 2.2 # 1.1
        bodyDistance = 4 # 1.1
        for i in range(4):
            w = loader.loadModel("%s/wheel" % self.modelpath)
            if i == 2 or i == 3:
                w.setHpr(0,180,0)
                w.flattenLight()
            self.wheels.append(w)
            #self.wheels[i].setColor(1,0.5,0.5)
            self.wheels[i].setScale(1,1,2)
            self.wheels[i].setQuat(Quat(0.7,0,0.7,0))
            self.wheels[i].reparentTo(render)
        self.wheels[0].setPos(pos.getX()-wheelDistance,pos.getY()+bodyDistance,pos.getZ()+bodyHeight)
        self.wheels[1].setPos(pos.getX()-wheelDistance,pos.getY()-bodyDistance,pos.getZ()+bodyHeight)
        self.wheels[2].setPos(pos.getX()+wheelDistance,pos.getY()+bodyDistance,pos.getZ()+bodyHeight)
        self.wheels[3].setPos(pos.getX()+wheelDistance,pos.getY()-bodyDistance,pos.getZ()+bodyHeight)

        for i in range(4):
            if i == 0 or i == 2:
                surfacetype = 1
            else:
                surfacetype = 2
            wheels_ode = odebase.ODEcylinder2(world, space, self.wheels[i], None, 2, 2, 1, 0.4, surfacetype, collidebit, catbit)
            odeworld.AddObject(wheels_ode)
            self.objects.append(wheels_ode)
            self.wheels_ode.append(wheels_ode)

            joint = OdeHinge2Joint(world)
            self.joints.append(joint)
            joint.attachBodies(self.carbody_ode.body, wheels_ode.body)
            #min/max angle for the wheel. Set min=max for stable turn
            joint.setParamHiStop(0, 0.0)
            joint.setParamLoStop(0, 0.0)

            #Error reduction parameter of suspension
            joint.setParamSuspensionERP(0, 0.9)

            #Blending of forces - in this case influences rigidity of a suspension
            joint.setParamSuspensionCFM(0, 0.001)

            #axis of joint: set one - vertical, and one - horisontal
            joint.setAxis1(0,0,1)
            joint.setAxis2(1,0,0)

        self.joints[0].setAnchor(Vec3(pos.getX()-(wheelDistance-0.2),pos.getY()+bodyDistance,pos.getZ()+bodyHeight))
        self.joints[1].setAnchor(Vec3(pos.getX()-(wheelDistance-0.2),pos.getY()-bodyDistance,pos.getZ()+bodyHeight))
        self.joints[2].setAnchor(Vec3(pos.getX()+(wheelDistance-0.2),pos.getY()+bodyDistance,pos.getZ()+bodyHeight))
        self.joints[3].setAnchor(Vec3(pos.getX()+(wheelDistance-0.2),pos.getY()-bodyDistance,pos.getZ()+bodyHeight))

        self.maxVelocity = 65
        self.maxSpeed=50
        self.accForce=500
        self.axis=[1,3]
        self.axis2=[1,3,0,2]

        self.ShowSpeedMeter()
        self.setupCamera()
        self.SetupParticle()
        self.confirmdead = False

        if odeEventHandler != None and self.odeworld.supportEvent:
            self.odeworld.setCollisionNotifier(self.carbody_ode, odeEventHandler)
            for b_ode in self.wheels_ode:
                self.odeworld.setCollisionNotifier(b_ode, odeEventHandler)

        self.audio = CarAudio1(self.carbody)

    def startEngine(self):
        self.audio.start()
        self.startenginetasks = Sequence(
                Wait(4.5),
                Func(self.smoke, True, True),
                Wait(4),
                Func(self.smoke, True, False))
        self.startenginetasks.start()


    def changeCameraMode(self, mode):
        self.cameramode = mode

    def toggleCameraMode(self):
        self.cameramode = (self.cameramode + 1) % 3


    def changeCarColor(self, color):
        material = self.npBody.findMaterial("*")
        #material = Material(material)
        material.setDiffuse(color)
        material.setAmbient(color)
        self.npBody.setMaterial(material, 1)

    def changeHeadLights(self, on):
        if on:
            tex = self.lightsTexture2
        else:
            tex = self.lightsTexture1
        self.lights[0].setTexture(tex,1)
        self.lights[1].setTexture(tex,1)

    def changeRearLights(self, on):
        if on:
            tex = self.lightsTexture2
        else:
            tex = self.lightsTexture1
        self.lights[2].setTexture(tex,1)
        self.lights[3].setTexture(tex,1)

    def setSyncCamera(self, syncCamera):
        self.syncCamera = syncCamera

    def setupCamera(self):
        #Setup the camera basis
        self.camPosNode = self.carbody.attachNewNode('camPosNode')
        self.camPosNode.setPos(0,6,-2)
        self.camLookatNode = self.carbody.attachNewNode('camLookatNode')
        self.camLookatNode.setPos(0,0,2)
        self.camLookatNode2 = self.carbody.attachNewNode('camLookatNode2')
        self.camLookatNode2.setPos(0,8,3.5)
        self.camDriverNode = self.carbody.attachNewNode('camDriverNode')
        self.camDriverNode.setPos(0,0,4)
        #base.camLens.setFar(10000)


    def ShowSpeedMeter(self):
        #spedometer
        self.spdm = OnscreenImage(image = '%s/spdm.png' % self.modelpath, scale=0.25, pos = (1, 0, -0.6))
        self.spdm.setTransparency(TransparencyAttrib.MAlpha)
        self.pointer = OnscreenImage(image = '%s/spdm_pointer.png' % self.modelpath, scale=0.25, pos = (1, 0, -0.6))
        self.pointer.setTransparency(TransparencyAttrib.MAlpha)
        self.lastPos = Vec3(0,0,0)


    def forward(self):
        self.Accel(self.maxVelocity, 40.0, self.axis)

    def normal(self):
        self.Accel(0, 15.0, self.axis2)

    def releasebrake(self):
        self.normal()
        self.changeRearLights(False)


    def backward(self):
        self.Accel(-25.0, 40.0, self.axis)

    def brake(self, force=200.0):
        self.Accel(0, force, self.axis2)
        self.changeRearLights(True)

    def Destroy(self):
        if hasattr(self, "startenginetasks"):
            self.startenginetasks.finish()
        self.audio.Destroy()
        for particle in self.particles:
            particle.disable()
            particle.cleanup()
        taskMgr.remove("ode car task")
        #taskMgr.remove("checkRotation")
        for joint in self.joints:
            joint.detach()
            joint.destroy()
        for b_ode in self.objects:
            self.odeworld.RemoveObject(b_ode)
            b_ode.destroy()
        self.objects = []
        self.spdm.destroy()
        self.pointer.destroy()

    def myTasks(self, task):
        self.TurnTask(task)
        if not self.confirmdead:
            self.JetTask(task)
            self.checkRotation(task)
            if self.IsDead():
                self.brake()
                self.confirmdead = True
                #self.releasebrake()
                self.cameramode = self.CAMERA_DEFAULT_MODE
                self.smoke(False, True)
        else:
            self.audio.setState(True, 0, False, 0)
        self.Sync()
        return task.cont

    #def addCamdist(self, v):
    #  self.camDistance += v


    def Accel(self, aspect, force, axis):
        if not self.allowTurnover and self.carOrientation < 0:
            self.acceleration = False
            return
        for i in [1,3,0,2]:
            self.joints[i].setParamFMax(1, 0)
        #We use two different methods for move forward and backward
        #Forward - "jet engine" - add force to the body of the car
        #Backward - angular engine - add angular speed to the wheels
        if aspect>0:
            self.acceleration=True
            self.stoppingforce = 0
        else:
            self.acceleration=False
            self.stoppingforce = force
            for i in axis:
                #set angular engine speed
                self.joints[i].setParamVel(1,aspect*self.carOrientation)
                #and force to it
                self.joints[i].setParamFMax(1, force)

    #check car orientation, and change control according to it
    def checkRotation(self,task):
        oldO=self.carOrientation
        if abs(int(self.carbody.getR()))<90:
            self.carOrientation=1
        else:
            self.carOrientation=-1
        if oldO != self.carOrientation:
            self.camPosNode.setZ(-self.camPosNode.getZ())
            if self.allowTurnover:
                for i in [1,3,0,2]:
                    self.joints[i].setParamVel(1,-self.joints[i].getParamVel(1))

        return task.again

    #turn wheels - set variables
    def Turn(self,enabled,aspect):
        self.turn=enabled
        self.turnspeed=aspect

    #immediately, turn wheels here
    def TurnTask(self,task):
        #calculate angle
        if not self.turn:
            if self.turnangle>0:
                self.turnspeed=-0.01*self.carOrientation
            if self.turnangle<0:
                self.turnspeed=0.01*self.carOrientation
            if -0.01<self.turnangle<0.01:
                self.turnangle=0;
        self.turnangle=self.turnangle+self.turnspeed*self.carOrientation
        if self.turnangle>0.3:
            self.turnangle=0.3
        if self.turnangle<-0.3:
            self.turnangle=-0.3
        # and set angle to the front wheels
        self.joints[0].setParamHiStop(0, self.turnangle)
        self.joints[0].setParamLoStop(0, self.turnangle)
        self.joints[2].setParamHiStop(0, self.turnangle)
        self.joints[2].setParamLoStop(0, self.turnangle)
        # will fix wheel position a bit better
        for i in xrange(4):
          self.wheels_ode[i].body.setFiniteRotationAxis(self.joints[i].getAxis2())
        return task.cont

    #task for jet engeene
    def JetTask(self,task):
        dir = self.carbody.getMat().getRow3(1)
        body = self.carbody_ode.body
        v = body.getLinearVel()
        fSameDirection = (dir.dot(v) >= 0)
        vl = v.length()
        self.audio.setState(self.confirmdead, vl, self.acceleration, self.stoppingforce)
        if self.acceleration:
            if self.maxSpeed > vl:
                body.addRelForce(0,self.accForce,0)
                if vl < 20 and fSameDirection:
                #if vl < 20:
                    self.smoke(True, True)
                    return task.cont
        self.smoke(True, False)
        return task.cont

    def IsDead(self):
        if not self.allowTurnover and self.carOrientation < 0:
            body = self.carbody_ode.body
            v = body.getLinearVel().length()
            if v < 0.1:
                return True
        return False

    def Sync(self):
        # update the camera
        if self.syncCamera:
            body = self.carbody_ode.body
            camVec = self.camPosNode.getPos(render) - body.getPosition()

            if self.cameramode == self.CAMERA_DRIVER_MODE:
                camLookat = self.camLookatNode2.getPos(render)
                targetCamPos = self.camDriverNode.getPos(render)
            else:
                if self.cameramode == self.CAMERA_DEFAULT_MODE:
                    camDistance = Vec2(-5, 0)
                else:
                    camDistance = Vec2(-5, -2)
                targetCamPos = body.getPosition() + camVec * camDistance.getX() + Vec3(0,0,camDistance.getY())
                camLookat = self.camLookatNode.getPos(render)

                if self.cameramode == self.CAMERA_DEFAULT_MODE:
                    dPos = targetCamPos - base.camera.getPos(render)
                    dt = globalClock.getDt()
                    #print targetCamPos, dPos, dt
                    delta = dPos * dt * 2
                    if delta.length() > 10:
                        delta *= delta.length() / 10
                    targetCamPos = (base.camera.getPos(render) + delta)
            if targetCamPos.getZ() < 1:
                targetCamPos.setZ(1)
            base.camera.setPos(targetCamPos)
            base.camera.lookAt(camLookat)

        # the speedometer pointer
        curPos = self.carbody.getPos(render)
        vel = (self.lastPos - curPos).length() * 6000 / self.maxVelocity
        self.lastPos = curPos
        dr=vel-self.pointer.getR()-30
        if dr>30:
            dr=30
        dr=dr*0.1
        self.pointer.setR(self.pointer.getR()+dr)

    def SetupParticle(self):
        particleRenderNode = render.attachNewNode("smokeNode")
        self.particles = []
        for i in range(3):
            particle = ParticleEffect()
            self.particles.append(particle)
            if i == 2:
                particle.loadConfig(Filename("share/particles/steam.ptf"))
            else:
                particle.loadConfig(Filename("demo_odecar1/particles/smoke2.ptf"))
            p0 = particle.getParticlesNamed('particles-1')
            p0.setBirthRate(100000)
            if i < 2:
                particle.start(self.npTubes[i], particleRenderNode)
            else:
                particle.start(self.carbody, particleRenderNode)
        particleRenderNode.setBin('fixed', 0)
        particleRenderNode.setDepthWrite(False)

    def smoke(self, tube, on):
        if tube:
            l  = [0, 1]
        else:
            l = [2]
        if on:
            #h = (self.actor.neck.getR()) / 180 * math.pi
            h = 0
            for i in l:
                particle = self.particles[i]
                p0 = particle.getParticlesNamed('particles-1')
                p0.setBirthRate(0.3 + 0.2 * random())
                emitter = p0.getEmitter()
                v = 1
                emitter.setExplicitLaunchVector(Vec3(v * math.sin(h), -v * math.cos(h), 12.0000))
        else:
            for i in l:
                particle = self.particles[i]
                p0 = particle.getParticlesNamed('particles-1')
                p0.setBirthRate(100000.0)


from direct.showbase.Audio3DManager import Audio3DManager
from pandac.PandaModules import AudioManager
class CarAudio1():
    STATE_START = 1
    STATE_READY = 2
    STATE_RUN = 3
    STATE_DEAD = 4
    def __init__(self, car, f3D=False):
        self.f3D = f3D
        self.car = car
        self.start0_sound = loader.loadSfx("audio/startengine0_11025.wav")
        self.start1_sound = loader.loadSfx("audio/startengine1_11025.wav")
        self.start1_sound.setLoop(1)
        self.run_sound = loader.loadSfx("audio/enginerun_11025.wav")
        self.run_sound.setLoop(1)
        self.normal_sound = loader.loadSfx("audio/enginenormal_11025.wav")
        self.normal_sound.setLoop(1)
        self.brake_sound = loader.loadSfx("audio/brake_11025.wav")
        self.brake_sound.setLoop(1)
        self.audioMgr = base.sfxManagerList[0]
        #self.audioMgr.audio3dSetDropOffFactor(5)
        if self.f3D:
            self.audio3d = Audio3DManager(self.audioMgr, camera)
            #self.audio3d.setDropOffFactor( 10 )
            #self.audio3d.attachSoundToObject(self.start0_sound, self.car)
            self.audio3d.attachSoundToObject(self.start1_sound, self.car)
            self.audio3d.attachSoundToObject(self.normal_sound, self.car)
            self.audio3d.attachSoundToObject(self.run_sound, self.car)
            self.audio3d.attachSoundToObject(self.brake_sound, self.car)
        self.state = self.STATE_START
        self.tasks = Sequence(
            Func(self.start0_sound.play),
            Wait(self.start0_sound.length()),
            Func(self.ready))

    def stopAll(self):
        self.start0_sound.stop()
        self.start1_sound.stop()
        self.run_sound.stop()
        self.normal_sound.stop()
        self.brake_sound.stop()
        self.brake_sound_playing = False

    def start(self):
        self.stopAll()
        self.tasks.start()

    def ready(self):
        if self.state != self.STATE_READY:
            self.stopAll()
            self.state = self.STATE_READY
            self.start1_sound.setVolume(0.8)
            self.start1_sound.play()

    def dead(self):
        if self.state != self.STATE_DEAD:
            self.stopAll()
            self.state = self.STATE_DEAD

    def run(self, speed, acceleration, stoppingforce):
        r = min(speed/100,1)

        minrate = 0.5
        pr = minrate + r * (1.5-minrate)
        self.normal_sound.setPlayRate(pr)

        minv = 0.1
        v = minv + r * (1-minv)
        self.normal_sound.setVolume(v)

        if self.state != self.STATE_RUN:
            self.acceleration = False
            self.start1_sound.stop()
            self.normal_sound.play()
            self.state = self.STATE_RUN

        if False:
            if self.acceleration != acceleration:
                if acceleration:
                    self.acceleration = acceleration
                    self.run_sound.play()
                    self.run_sound.setVolume(v)
                else:
                    vold = self.run_sound.getVolume()
                    if vold < 0.1:
                        self.acceleration = acceleration
                        self.run_sound.stop()
                    else:
                        self.run_sound.setVolume(vold - 0.05)

        if not acceleration and speed > 1 and stoppingforce > 20:
            v = r * (stoppingforce-20) / 100
            if v < 0.1:
                if self.brake_sound_playing:
                    self.brake_sound.stop()
                    self.brake_sound_playing = False
            else:
                if not self.brake_sound_playing:
                    self.brake_sound.play()
                    self.brake_sound_playing = True
                v = min(v*2,1)
                self.brake_sound.setVolume(v)
        elif self.brake_sound_playing:
            self.brake_sound.stop()
            self.brake_sound_playing = False


    def setState(self, isdead, speed, acceleration, stoppingforce):
        if self.state != self.STATE_START:
            if isdead:
                self.dead()
            elif speed > 0.5:
                self.run(speed, acceleration, stoppingforce)
            else:
                self.ready()
        self.update()

    def Destroy(self):
        self.tasks.finish()
        if self.f3D:
            #self.audio3d.detachSound(self.start0_sound)
            self.audio3d.detachSound(self.start1_sound)
            self.audio3d.detachSound(self.normal_sound)
            self.audio3d.detachSound(self.run_sound)
            self.audio3d.detachSound(self.brake_sound)
        self.stopAll()
        #self.audioMgr.stopAllSounds()

    def update(self):
        if self.f3D:
            self.audio3d.update()
