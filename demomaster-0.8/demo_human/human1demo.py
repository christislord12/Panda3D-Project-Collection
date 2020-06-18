
from random import randint, random
import math, sys
import demobase, camerabase, skydome2, geomutil, splashCard

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2,Mat4,VBase3
from pandac.PandaModules import Shader, Texture, TextureStage
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Func, Wait

#from direct.particles.Particles import Particles
#from direct.particles.ParticleEffect import ParticleEffect

from direct.actor.Actor import Actor
import david, posemanager, animationmanager


useShadowManager = 0
useSpotLight = False

if useShadowManager == 1:
   from shadowManager import ShadowManager
elif useShadowManager == 2:
   from shadowManager2 import ShadowManager
elif useShadowManager == 3:
    import PSSM.ParallelSplitShadowMap

####################################################################################################################

class Human1Demo(demobase.DemoBase):
    """
    Human - 1
    MakeHuman Model Tester
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        splash=splashCard.splashCard('textures/loading.png')
        base.setBackgroundColor(0.0, 0.0, 0.5)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()
        self.animationMgr = animationmanager.AnimationManager()
        self.setupShadowManager()

        self.selection = None
        self.togglaAnimation("Breath", True)
        self.togglaAnimation("Blink", True)

        # for closeup distances toggle
        self.distanceindex = 0
        self.distances = [24,16,10,6,3]
        self.jointselection = None

        self.hair = False
        splash.destroy()

    def setupShadowManager(self):
        if useShadowManager == 1:
            self.att_sMgr = ShadowManager(render, ambient=0.1,hardness=20,fov=40) #,blur=True,SIZE=1024)
            self.att_sMgr.changeLightPos(Vec3(5,-16,30),self.human.model.getPos())
            self.att_sMgr.setStandardControl()
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

    #def changeLight(self, object):
    #    if useShadowManager == 2:
    #        self.att_sMgr.changeLightPos(self.att_Light.att_position.getValue(), self.human.model.getPos())

    def SetupCamera(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-500,-500,-200], [500,500,200],
                     [-45,45, 0],
                     [0,0,0],
                     #Vec3(0,-33,13.5),
                    Vec3(0,0,8.5),
                     rate=0.3, speed=20, distance=37)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.ShowPosition(self.textnode)
        #self.att_cameracontrol.LockAt((0,0,0))
        self.att_cameracontrol.Stop()
        #self.att_cameracontrol.LockPosition()

    	#demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)
        #taskMgr.add(self.cameraUpdated, "camupdate")


    def LoadLights(self):
        if useShadowManager == 0 or useShadowManager == 2:
            if useSpotLight:
                self.att_Light = demobase.Att_spotLightNode(False, "Light:Spotlight",
                    Vec4( 1,1,1, 1 ), 88, 28.0,
                    Vec3(5,-16,30),
                    Point3(0,0,10),
                    #attenuation=Vec3( 1, 0.0, 0.0 ))
                    attenuation=Vec3( 0, 0.03, 0.0 ))
                self.att_Light.setLight(render)
            else:
                self.att_Light = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                    Vec4( 1, 1, 1, 1 ), Vec3(5,-16,36),
                    attenuation=Vec3( 0.1, 0.03, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                    #node=self.lightpivot,
                    fBulb=True)
                #self.att_pointLight.att_bulb.setBulbSize(None, 1.4)
                #self.att_pointLight.att_bulb.setFireScale(None, 2)
                self.att_Light.setLight(render)
            #self.att_Light.setNotifier(self.changeLight)

            self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
            self.att_ambientLight.setLight(render)
            #self.att_ambientLight.setNotifier(self.changeLight)


    def LoadSkyBox(self):
        #self.att_skydome = skydome1.SkyDome1(render, texturefile='textures/clouds_bw.png')
        self.att_skydome = skydome2.SkyDome2(render)
        self.att_skydome.setStandardControl()
        self.att_skydome.att_skycolor.setColor(Vec4(0.3,0.3,0.3,1))
        self.att_skydome.setPos(Vec3(0,0,-400))


        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )


    def loadPoses(self):
        self.pr.Reset()
        filelist = [
            "basic1.pose",
            "basic2.pose",
            "basic3.pose",
            "app1.pose",
            ]
        dir = "demo_human/models/david1/pose/"
        ok, errinfo = self.pr.LoadFiles(self.human, dir, filelist)
        if not ok:
           self.showError("Pose Error: %s" % errinfo[0], errinfo[1])
           return False
        return True

    def LoadModels(self):
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)

        #self.LoadSkyBox()
        self.ground = geomutil.createPlane('myplane',100,100,1,1)
        self.ground.reparentTo(render)

        #self.ground.setShaderAuto()
        #self.ground.setLightOff()

        #groundtex = loader.loadTexture("textures/grass.png")
        groundtex = loader.loadTexture("textures/dirt.png")
        self.ground.setTexture(groundtex)
        #self.ground.setLightOff()
        #self.ground.setColor(Vec4(0.1,0.2,0.1,1))
        #self.ground.setTexScale(TextureStage.getDefault(), 100,100)
        #self.ground.setTexScale(TextureStage.getDefault(), 10,10)

        self.LoadHuman()


    def LoadHuman(self):
        self.human = david.David()
        self.animationok = False
        if self.human.Load():
            self.human.model.setZ(9)
            self.pr = posemanager.PoseRepository()
            #ok, err = self.pr.ReadFile("demo_human/models/david1/pose/basic1.pose")
            ok = self.loadPoses()
            if not ok:
                #self.parent.ShowSource(text=err, nosave=True)
                #print err
                #self.showError("Pose Error", err)
                self.ar = None
                pass
            else:
                self.ar = animationmanager.AnimationRepository(self.pr)
                ok, err = self.ar.ReadFile(self.human, "demo_human/models/david1/pose/animation1.ani")
                if not ok:
                    #self.parent.ShowSource(text=err, nosave=True)
                    #print err
                    self.showError("Animation Error", err)
                else:
                    self.animationok = True

            self.human.model.reparentTo(render)

            for joint in self.human.jointlist:
                np = self.human.joints[joint].np
                hpr = np.getHpr()
                vjointname = joint.replace(".", "_")
                expr = "v = self.att_J_%s = demobase.Att_Vecs(False,'Joint:%s',3,Vec3(%f,%f,%f),-360,360,2)" % (vjointname, joint,hpr[0],hpr[1],hpr[2])
                exec(expr)
                v.default = hpr
                v.jointname = joint
                v.setNotifier(self.setJointHpr)

            for joint in self.human.pjointlist:
                np = self.human.pjoints[joint].np
                pos = np.getPos()
                vjointname = joint.replace(".", "_")
                expr = "v = self.att_PJ_%s = demobase.Att_Vecs(False,'PJoint:%s',3,Vec3(%f,%f,%f),-2,2,2)" % (vjointname, joint,pos[0],pos[1],pos[2])
                exec(expr)
                v.default = pos
                v.jointname = joint
                v.setNotifier(self.setJointPos)
            #self.human.model.setShaderOff()


    def setJointHpr(self, object):
        self.human.joints[object.jointname].np.setHpr(object.getValue())

    def setJointPos(self, object):
        self.human.pjoints[object.jointname].np.setPos(object.getValue())

    def resetJointPos(self):
        for joint in self.human.jointlist:
            np = self.human.joints[joint].np
            jointname = joint.replace(".", "_")
            exec("v = self.att_J_%s" % (jointname))
            np.setHpr(v.default)
            v.setValue(v.default)
        for joint in self.human.pjointlist:
            np = self.human.pjoints[joint].np
            jointname = joint.replace(".", "_")
            exec("v = self.att_PJ_%s" % (jointname))
            np.setPos(v.default)
            v.setValue(v.default)

    def syncJointPos(self):
        for joint in self.human.jointlist:
            np = self.human.joints[joint].np
            jointname = joint.replace(".", "_")
            exec("v = self.att_J_%s" % (jointname))
            hpr = np.getHpr()
            v.setValue(hpr)
        for joint in self.human.pjointlist:
            np = self.human.pjoints[joint].np
            jointname = joint.replace(".", "_")
            exec("v = self.att_PJ_%s" % (jointname))
            pos = np.getPos()
            v.setValue(pos)

    def ClearScene(self):
        if useShadowManager > 0:
            self.att_sMgr.Destroy()
            taskMgr.remove("updateShadowManager")
        #taskMgr.remove("camupdate")
        self.animationMgr.Destroy()

        if hasattr(self, "att_skydome"):
            self.att_skydome.Destroy()

        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def Demo01(self):
        """Reset Joint Positions"""
        self.resetJointPos()

    def Demo02(self):
        """Reload Poses"""
        self.reloadPose()

    def Demo03(self):
        """Reload Animations"""
        self.reloadAnimation()

    def Demo04(self):
        """Sync Joints"""
        self.syncJointPos()

    def Demo05(self):
        """Pose Selector"""
        if self.reloadPose():
            ret, selection = self.parent.GetListSelector("Select Pose", self.pr.GetPoseList())
            if ret:
                self.pr.setPose(self.human, selection)
                self.selection = selection
                self.syncJointPos()

    def Demo06(self):
        """Reload Selected Pose"""
        if self.reloadPose() and self.selection != None:
            self.pr.setPose(self.human, self.selection)
            self.syncJointPos()


    def Demo07(self):
        """Closeup to Joint"""
        jointlist = []
        for l in [self.human.joints,self.human.pjoints]:
            for joint in l:
                if joint not in jointlist:
                    jointlist.append(joint)
        ret, selection = self.parent.GetListSelector("Select Joint", jointlist)
        if ret:
            self.jointselection = selection
            self.closeup(selection)

    def closeup(self, selection):
        np = self.human.model.exposeJoint(None, 'modelRoot', selection)
        pos = np.getPos(render)
        self.att_cameracontrol.SetFocus(pos,dir=Vec3(0,1,0),distance=self.distances[self.distanceindex])

    def Demo08(self):
        """Closer"""
        #if self.jointselection != None:
        #    self.distanceindex = (self.distanceindex + 1) % len(self.distances)
        #    self.closeup(self.jointselection)
        self.distanceindex = (self.distanceindex + 1) % len(self.distances)
        self.att_cameracontrol.SetDistance(self.distances[self.distanceindex])

    def Demo09(self):
        """Toggle Hair"""
        self.hair = not self.hair
        self.human.setupHair(self.hair)


    def Demo11(self):
        "Toggle - Animation 1"
        name = "Animation1"
        self.togglaAnimation(name, False)

    def Demo12(self):
        "Toggle - Breath"
        name = "Breath"
        self.togglaAnimation(name, True)

    def Demo13(self):
        "Toggle - Dive"
        name = "Dive"
        self.togglaAnimation(name, False)

    def Demo14(self):
        "Toggle - Blink"
        name = "Blink"
        self.togglaAnimation(name, True)

    def Demo15(self):
        "Normal Face"
        name = "NormalFace"
        self.showExpression(name)

    def Demo16(self):
        "Happy"
        name = "HappyFace"
        self.showExpression(name)

    def Demo17(self):
        "Sad"
        name = "SadFace"
        self.showExpression(name)

    def Demo18(self):
        "Very Sad"
        name = "VerySadFace"
        self.showExpression(name)

    def Demo19(self):
        "Worried"
        name = "Worried"
        self.showExpression(name)

    def Demo20(self):
        "Smart"
        name = "Smart.L"
        self.showExpression(name)

    def Demo21(self):
        "Expression 1"
        name = "Expression1"
        self.showExpression(name)

    def Demo41(self):
        "B"
        name = "Say.BI"
        self.showExpression(name)

    def showExpression(self, expression):
        lookat = Point3(0,0,16)
        if useShadowManager == 0:
            if useSpotLight:
                self.att_Light.att_lookAt.setValue(lookat)
        elif useShadowManager == 1:
            self.att_sMgr.changeLightPos(None, lookat)

        self.distanceindex = 1
        self.closeup("Mouth.U")
        if expression != None:
            self.togglaAnimation(expression, False)


    def reloadPose(self):
        return self.loadPoses()

    def reloadAnimation(self):
        self.animationMgr.clearAll()
        ok, err = self.ar.Reload(self.human)
        if not ok:
            self.showError("Animation Error", err)
        return ok

    def showError(self, title, err):
        print err
        self.parent.MessageBox(title, err)


    def togglaAnimation(self, name, loop):
        if self.ar == None:
            return
        animation = self.animationMgr.getAnimation(name)
        if animation == None or not loop:
            animation = self.ar.createAnimation(self.human, name)
            animation.start(loop=loop)
            self.animationMgr.add(animation)
        else:
            if animation.isRunning():
                animation.stop()
            else:
                animation.resume()



    def Demo91(self):
        """Wired frame Body"""
        np = self.human.model.find("**/Body")
        np.setRenderModeWireframe()

    def Demo92(self):
        """Filled Body"""
        np = self.human.model.find("**/Body")
        np.setRenderModeFilled()


########################################################
##    def Demo32(self):
##        "Pose test 1"
##        ok, err = self.pr.Reload()
##        if not ok:
##            print err
##        else:
##            self.pr.setPose("F.Close.L")
##            self.pr.setPose("F.Close.R")
##
##    def Demo33(self):
##        "Pose test 2"
##        ok, err = self.pr.Reload()
##        if not ok:
##            print err
##        else:
##            self.pr.setPose("F.Open.L")
##            self.pr.setPose("F.Open.R")
##
##
##    def Demo34(self):
##        "Animation test 1"
##        ok, err = self.pr.Reload()
##        if not ok:
##            print err
##        else:
##            ok, err = self.ar.Reload()
##            if not ok:
##                print err
##            else:
##                self.animation = self.ar.createAnimation("CloseFingerOneByOne")
##                self.animation.start()
##                #animation.update(0)
##                self.animation.update(0.5)
##                #animation.update(1)
##
##    def Demo35(self):
##        "time move"
##        self.animation.update(0.5)
