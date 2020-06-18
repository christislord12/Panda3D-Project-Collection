###########################################################
# Estrada Real Digital
# DCC - UFMG
###########################################################

import math

from pandac.PandaModules import *
from pandac.PandaModules import Point3, Vec3
#from direct.showbase.DirectObject import DirectObject

import FrustumPart
import demobase

MAXSPLITS = 4
#SPLIT_DISTANCE = 500.0
FILMSIZE_SCALE = 1.1
SHADER_DIR = 'PSSM/'


class ParallelSplitShadowMap(demobase.Att_base):

    def __init__(self, lightDirection, lightsQuality = [2048, 2048, 1024], pssmBias = 0.8, pushBias = 0.03, lightColor = VBase3(0.125, 0.149, 0.160), lightIntensity = 0.8):
        demobase.Att_base.__init__(self, False, "PSSM")

        self.lightDirection= lightDirection
        self.lightDirection.normalize()
        self.lightsQuality = lightsQuality

        self.pssmBias = pssmBias
        self.pushBias= pushBias
        self.lightColor= lightColor
        self.lightIntensity = lightIntensity
        self.rotation = 0
        #self.debugColors = True
        self.debugColors = False


        base.cam.setShaderOff(1)
        base.cam.setColor(1,1,1)

#        loadPrcFileData('','copy-texture-inverted 1')

        self.createFrustumParts()
        self.calculateViewFrustumDepths()
        #self.toggleDebug()
        self.setUpShader()
        self.adjustCameraFar()
        #self.setUpControls()


        #Temp
        #render.setTwoSided(True)
        #render2d.hide()
        #aspect2d.hide()


##    def setUpControls(self):
##        self.accept( 'f5', render.setShaderOff)
##        self.accept( 'f6', base.bufferViewer.toggleEnable)
##        self.accept( 'f7', self.toggleDebug)
##
##        self.accept( 'insert-repeat', self.changeSunPosition, [+0.1])
##        self.accept( 'delete-repeat', self.changeSunPosition, [-0.1])
##
##        self.accept( 'home-repeat', self.changePSSMBias, [+0.01])
##        self.accept( 'end-repeat', self.changePSSMBias, [-0.01])
##
##        self.accept( 'page_up-repeat', self.changePushBias, [+0.01])
##        self.accept( 'page_down-repeat', self.changePushBias, [-0.01])

    def setShaderInput(self):
        color = self.lightColor * self.lightIntensity
        render.setShaderInput('lightColor',color.getX(),color.getY(),color.getZ(),0.0)
        render.setShaderInput('push',self.pushBias,self.pushBias,self.pushBias,0)
        render.setShaderInput('scale',1,1,1,1)
        render.setShaderInput('lightDirection',self.lightDirection.getX(), self.lightDirection.getY(), self.lightDirection.getZ(), 0)
        render.setShaderInput('debugColors', self.debugColors, 0, 0, 0)

    def setUpShader(self):
        mci = NodePath("Main Camera Initializer")
        if (base.win.getGsg().getSupportsShadowFilter()):
            shaderfile = '%spssm-shadow.sha' % SHADER_DIR
        else:
            shaderfile = '%sshadow-nosupport.sha' % SHADER_DIR
        shader = loader.loadShader(shaderfile)
        mci.setShader(shader)
        base.cam.node().setInitialState(mci.getState())

        self.setShaderInput()
##        color = self.lightColor * self.lightIntensity
##        render.setShaderInput('lightColor',color.getX(),color.getY(),color.getZ(),0.0)
##        render.setShaderInput('push',self.pushBias,self.pushBias,self.pushBias,0)
##        render.setShaderInput('scale',1,1,1,1)
##        render.setShaderInput('lightDirection',self.lightDirection.getX(), self.lightDirection.getY(), self.lightDirection.getZ(), 0)
##        render.setShaderInput('debugColors', self.debugColors, 0, 0, 0)

        #Depth maps
        for i in range(0, MAXSPLITS+1):
            if(i < len(self.lightsQuality)):
                render.setShaderInput('depthmap'+str(i),self.frustumParts[i].depthmap)
                render.setShaderInput('light'+str(i),self.frustumParts[i].cam)

            else:
                render.setShaderInput('depthmap'+str(i),self.frustumParts[0].depthmap)
                render.setShaderInput('light'+str(i),self.frustumParts[0].cam)



    #Make sure that the camera contain the visible scene as tight as possible
    def adjustCameraFar(self):
#        base.cam.node().getLens().setFar(2.0*render.getBounds().getRadius())
        base.cam.node().getLens().setFar(2000)


    def createFrustumParts(self):
        self.frustumParts = []
        for i in range(0, len(self.lightsQuality)):
            self.frustumParts.append(FrustumPart.FrustumPart(i, self.lightsQuality[i]))

    def calculateViewFrustumDepths(self):

        for i in range(0, len(self.lightsQuality)):
            self.frustumParts[i].calculateDepth(i, len(self.lightsQuality), self.pssmBias)

#            if(i == 0):
#                self.frustumParts[i].calculateDepth(i, len(self.lightsQuality), self.pssmBias, base.cam.node().getLens().getNear())
            if(i != 0):
                self.frustumParts[i-1].splitMaxDepth = self.frustumParts[i].splitMinDepth
            if(i == len(self.lightsQuality) -1):
                self.frustumParts[i].splitMaxDepth = base.cam.node().getLens().getFar()


        self.setUpDepths()

    def setUpDepths(self):
        #Depths of the splits
        if(len(self.lightsQuality) == 1):
            render.setShaderInput('depth',self.frustumParts[0].splitMaxDepth, 0, 0, 0)
        elif(len(self.lightsQuality) == 2):
            render.setShaderInput('depth',self.frustumParts[0].splitMaxDepth, self.frustumParts[1].splitMaxDepth, 0, 0)
        elif(len(self.lightsQuality) == 3):
            render.setShaderInput('depth',self.frustumParts[0].splitMaxDepth, self.frustumParts[1].splitMaxDepth, self.frustumParts[2].splitMaxDepth, 0)
        elif(len(self.lightsQuality) == 4):
            render.setShaderInput('depth',self.frustumParts[0].splitMaxDepth, self.frustumParts[1].splitMaxDepth, self.frustumParts[2].splitMaxDepth, self.frustumParts[3].splitMaxDepth)



    def update(self):

        for i in range(0, len(self.lightsQuality)):

            self.splitViewFrustum(i)

#            self.frustums[i].cam.setPos(base.cam.getPos() + self.lightDirection*100)

#            self.updateFrustrumPoints(i, base.cam.getPos(), base.cam.getQuat(render).getAxis())






    def splitViewFrustum(self, i):

        #Step 1: calculate the split/light width,height
        height = 2.0 * math.tan(math.radians(base.cam.node().getLens().getFov().getX()) * 0.5) * self.frustumParts[i].splitMaxDepth
        width = height * base.cam.node().getLens().getAspectRatio()
        self.frustumParts[i].cam.node().getLens().setFilmSize((width*FILMSIZE_SCALE), (height*FILMSIZE_SCALE))

        #Step 2: Calculate the split/light far
        #TODO

        #Step 3: Calculate the split/light position
        centerPosition = Point3(0,1,0)*((self.frustumParts[i].splitMaxDepth + self.frustumParts[i].splitMinDepth) / 2.0)

        splitPosition = centerPosition - base.camera.getRelativeVector(render, self.lightDirection) * self.frustumParts[i].cam.node().getLens().getFar() / 2.0


        self.frustumParts[i].cam.setPos(base.camera, splitPosition)
        self.frustumParts[i].cam.lookAt(base.camera, centerPosition)




##    def toggleDebug(self):
##        if(self.debugColors):
##            self.debugColors = False
##
##            for i in range(0, len(self.lightsQuality)):
##                self.frustumParts[i].cam.node().hideFrustum()
##
##        else:
##            self.debugColors = True
##
##            for i in range(0, len(self.lightsQuality)):
##                self.frustumParts[i].cam.node().showFrustum()
##
##
##
##
##        render.setShaderInput('debugColors', self.debugColors, 0, 0, 0)
##
##
##    def changeSunPosition(self, angleIncrease):
##        self.rotation += angleIncrease
##
##        self.lightDirection.addX(math.sin(self.rotation))
##        self.lightDirection.addY(-math.cos(self.rotation))
##
##        self.lightDirection.normalize()
##        self.lightDirection.setZ(-1.0)
##
###        print 'New light direction: '+str(self.lightDirection)
##
##    def changePSSMBias(self, biasIncrease):
##        self.pssmBias += biasIncrease
##
##        if(self.pssmBias <= 0): self.pssmBias = 0
##
##        self.calculateViewFrustumDepths()
##
##        print 'New PSSMbias: '+str(self.pssmBias)
##
##
##
##    def changePushBias(self, biasIncrease):
##        self.pushBias += biasIncrease
##
##        print 'New pushBias: '+str(self.pushBias)
##
##
    def Destroy(self):
        base.cam.node().setInitialState(RenderState.makeEmpty())
        for i in range(0, len(self.lightsQuality)):
            self.frustumParts[i].Destroy()

    def setParams(self, object):
        self.pushBias = self.att_pushBias.v
        self.pssmBias = self.att_pssmBias.v
        self.lightDirection = self.att_lightDirection.getValue()
        self.lightDirection.normalize()
        self.lightColor = self.att_lightColor.getColor()
        self.lightIntensity = self.att_lightIntensity.v
        self.setShaderInput()

    def setStandardControl(self):
        self.att_pushBias = demobase.Att_FloatRange(False, "Push Bias", 0.0, 1, self.pushBias, 3)
        self.att_pushBias.setNotifier(self.setParams)
        self.att_pssmBias = demobase.Att_FloatRange(False, "Pssm Bias", 0.0, 1, self.pssmBias, 3)
        self.att_pssmBias.setNotifier(self.setParams)
        self.att_lightDirection = demobase.Att_Vecs(False,"Direction",3,self.lightDirection,-1,1,2)
        self.att_lightDirection.setNotifier(self.setParams)
        self.att_lightColor = demobase.Att_color(False, "Color", self.lightColor)
        self.att_lightColor.setNotifier(self.setParams)
        self.att_lightIntensity = demobase.Att_FloatRange(False, "Intensity", 0.0, 1, self.lightIntensity, 2)
        self.att_lightIntensity.setNotifier(self.setParams)
##        self.lightsQuality = lightsQuality
##
