import math, sys, random
from pandac.PandaModules import *
from direct.showbase import DirectObject
from direct.task import Task

# clcheung ported from:
# Legion - http://www.panda3d.org/phpbb2/viewtopic.php?t=3044
'''
////////////////////////////////////////////////////////////////////////////////
/// This lensFlare class implements a fairly simple lens-flare effect        ///
/// for an arbitrary number of lights (careful, though, can impact your FPS) ///
///                                                                          ///
/// special thanks to Treeform, who provided me with some sample code on the ///
/// functions that help to project everything into the 2D screen space       ///
///                                                                          ///
/// by Legion of Dynamic Discord                                             ///
////////////////////////////////////////////////////////////////////////////////
'''

class lensFlare:
    def __init__(self):
        self.mybuffer = base.win.makeTextureBuffer("My Buffer", 10, 10)
        self.mydata = PNMImage()
        self.mytexture = Texture()
        self.mybuffer.setSort(-100)
        self.mybuffer.addRenderTexture(self.mytexture, GraphicsOutput.RTMCopyRam)
        self.mycamera = base.makeCamera(self.mybuffer)
        #mycamera.node().setScene(render)
        self.mycamera.reparentTo(base.cam)
        distance = 130000.0
        #lens = base.cam.node().getLens()
        self.ortlens = OrthographicLens()
        self.ortlens.setFilmSize(10, 10) # or whatever is appropriate for your scene
        self.ortlens.setNearFar(1,distance)
        self.mycamera.node().setLens(self.ortlens)


        #Lights and effects will be stored in lists
        self.lightNodes = []
        self.effectNodes = []
        self.lightColor = []
        self.obscured = 0.0
        #keep a reference of nodePath and index for easier removing lens-flares later
        self.sourceNodes = {}

        #attach a node to the screen middle, used for some math
        self.mid2d = aspect2d.attachNewNode('mid2d')

        #start the task that implements the lens-flare
        taskMgr.add(self.flareTask, 'flareTask')
        self.threshold = 0.0
        self.radius = 0.8
        self.strength = 1.0
##  function to add a light source, where a lens-flare should be applied
    def addLight(self, nodePath, color):
        #append the lights nodepath to the lightNode list
        self.lightNodes.append(nodePath)
        self.lightColor.append(color)
        #create a nodepath that'll hold the texture cards for the new lens-flare
        newNodepath = aspect2d.attachNewNode('effectNode'+str(len(self.effectNodes)))
        newNodepath.attachNewNode('fakeHdr')
        newNodepath.attachNewNode('flareNode')

        #the models are really just texture cards create with egg-texture-cards from the actual pictures
        hdr = loader.loadModel('models/flare/flare.egg')
        hdr.reparentTo(newNodepath.find('**/fakeHdr'))
        flare0 = loader.loadModel('models/flare/reflex1.egg')
        flare1 = loader.loadModel('models/flare/reflex2.egg')
        flare2 = loader.loadModel('models/flare/reflex3.egg')
        flare0.setScale(.2)
        flare1.setScale(.2)
        flare2.setScale(.2)
        flare0.reparentTo(newNodepath.find('**/flareNode'))
        flare1.reparentTo(newNodepath.find('**/flareNode'))
        flare2.reparentTo(newNodepath.find('**/flareNode'))
        newNodepath.setTransparency(TransparencyAttrib.MAlpha)
        newNodepath.setBin('background', 0)
        newNodepath.setDepthWrite(0)
        self.effectNodes.append(newNodepath)

        self.sourceNodes[nodePath] = len(self.lightNodes)-1

        #print self.effectNodes[len(self.lightNodes)-1].ls()

## remove a previously added light source by its nodePath
    def remove(self, nodePath):
        index = self.sourceNodes[nodePath]
        self.lightNodes[index].removeNode()
        self.effectNodes[index].removeNode()
        del self.lightNodes[index]
        del self.effectNodes[index]

        del self.sourceNodes
        self.sourceNodes = {}
        for i in xrange(0, len(self.lightNodes)):
            key = self.lightNodes[i]
            self.sourceNodes[key] = i


## this function returns the aspect2d position of a light source, if it enters the cameras field of view
    def get2D(self, nodePath):
        #get the position of the light source relative to the cam
        p3d = base.cam.getRelativePoint(nodePath, Point3(0,0,0))
        p2d = Point2()

        #project the light source into the viewing plane and return 2d coordinates, if it is in the visible area(read: not behind the cam)
        if base.cam.node().getLens().project(p3d, p2d):
            return p2d
        return None

    def getObscured(self, index, color):
        r = self.lightNodes[index].getBounds().getRadius()
        self.ortlens.setFilmSize(r * self.radius, r * self.radius) # or whatever is appropriate for your scene

        self.mycamera.node().setLens(self.ortlens)
        self.mycamera.lookAt(self.lightNodes[index])
        base.graphicsEngine.renderFrame()
        self.mytexture.store(self.mydata)
        #print mydata.getXel(5,5)
        obscured = 100.0
        color = VBase3D(color[0],color[1],color[2])
        for x in xrange(0,9):
            for y in xrange(0,9):
                #print self.mydata.getXel(x,y), color
                #if self.mydata.getXel(x,y) == color:
                if color.almostEqual(self.mydata.getXel(x,y), self.threshold):
                    obscured -=  1.0

        return obscured

## the task that creates the lens flare effects
    def flareTask(self, task):
        #going through the list of lightNodePaths
        for index in xrange(0, len(self.lightNodes)):
            node = self.effectNodes[index]
            pos2d = self.get2D(self.lightNodes[index])

            #if the light source is visible from the cam's point of view, display the lens-flare
            if pos2d:
                obscured = self.getObscured(index, self.lightColor[index])
                #print obscured
                #length is the length of the vector that goes from the screen middle to the pos of the light
                length = math.sqrt(pos2d.getX()*pos2d.getX()+pos2d.getY()*pos2d.getY())
                #length gets smaller the closer the light is to the screen middle... but since I used length to
                #calculate the brightness of the effects, I actually need an inverse behaviour, since the brightness
                #will be greates when center of screen= pos of light
                length= 1.0-length*2
                obscured = obscured/100
                self.obscured = obscured
                length=length-obscured
                #print length, obscured
                if length < 0 and obscured > 0: length = 0.0
                if length < 0 and obscured <= 0: length = 0.3
                if length > 1  : length = 1

                if obscured >= 0.8:
                    node.find('**/reflex1').hide()
                    node.find('**/reflex2').hide()
                    node.find('**/reflex3').hide()
                    continue
                else:
                    node.find('**/reflex1').show()
                    node.find('**/reflex2').show()
                    node.find('**/reflex3').show()
                #drawing the lens-flare effect...
                r= self.lightColor[index].getX()
                g= self.lightColor[index].getY()
                b= self.lightColor[index].getZ()
                r = math.sqrt(r*r+length*length) * self.strength
                g = math.sqrt(g*g+length*length) * self.strength
                b = math.sqrt(b*b+length*length) * self.strength
                if obscured > 0.19:
                    a = obscured - .2
                else:
                    a = .4-length
                if a < 0 : a = 0
                if a > 0.8 : a = 0.8
                hdr = node.find('**/fakeHdr')
                hdr.setColor(r,g,b,0.8-a)
                hdr.setR(90*length)
                self.effectNodes[index].find('**/flareNode').setColor(r,g,b,0.5+length)
                hdr.setPos(pos2d.getX(),0,pos2d.getY())
                hdr.setScale(8.5+(5*length))
                vecMid = Vec2(self.mid2d.getX(), self.mid2d.getZ())
                vec2d = Vec2(vecMid-pos2d)
                vec3d = Vec3(vec2d.getX(), 0, vec2d.getY())
                node.find('**/reflex3').setPos(self.effectNodes[index].find('**/fakeHdr').getPos()-(vec3d*10))
                node.find('**/reflex2').setPos(self.effectNodes[index].find('**/fakeHdr').getPos()+(vec3d*5))
                node.find('**/reflex1').setPos(self.effectNodes[index].find('**/fakeHdr').getPos()+(vec3d*10))
                node.show()
                #print "a",a
            else:
                #hide the lens-flare effect for a light source, if it is not visible...
                node.hide()
        return Task.cont

    def Destroy(self):
        taskMgr.remove('flareTask')

        self.mycamera.node().setInitialState(RenderState.makeEmpty())
        self.mycamera.removeNode()
        self.mybuffer.clearRenderTextures()
        base.graphicsEngine.removeWindow(self.mybuffer)

        for node in self.effectNodes:
            node.removeNode()
