
from random import randint, random
import math, sys
import demobase, camerabase, geomutil,splashCard, psFilter

#import direct.directbase.DirectStart
from pandac.PandaModules import Filename, StringStream
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, loadPrcFileData,ConfigVariableBool
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3, Plane, MouseButton
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, PNMImage, RenderState,TransparencyAttrib
from direct.interval.LerpInterval import LerpFunc
from direct.actor.Actor import Actor

from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay,CollisionPlane
from pandac.PandaModules import GeoMipTerrain

SIZE=128
PSIZE=50.0
####################################################################################################################
class WaterVtf1DemoNew(demobase.DemoBase):
    """
    Nature - Water vtf 2 New
    Uses Vertex Texture for water surface, with terrain added
    Reference: NVidia SDK 9.5
    """
    BOATLEVEL = 0.7
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.load = False
        if ConfigVariableBool("basic-shaders-only").getValue():
            self.parent.MessageBox("Vertex Texture Fetching Demo",
            "This demonstration uses advance shader technique, which need to set the basic-shaders-only option to #f\nTo run this demo you need a powerful video card, and run demomaster by:\ndemomaster.py f\n"
            )
            return
        self.load = True

        splash=splashCard.splashCard('textures/loading.png')
        #base.setBackgroundColor(0.5, 0.2, 0.2)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
#        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
#                     [-100,-100,-100], [100,100,100], [-45,45, -17], [0,0,45],
#                     Vec3(48,-48,21),
#                     rate=0.2)
#        self.att_cameracontrol.DefaultController()
#        self.att_cameracontrol.ShowPosition(self.textnode)
##        self.att_cameracontrol.Stop()
        #self.SetCameraPos(Vec3(0,-54,36), Vec3(0,-36,0))
        self.SetCameraPos(Vec3(0,-54,36), Vec3(0,-3,0))
        base.disableMouse()

    	#demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.timer, 'mytimer')

        self.setupWaterPlane()
        render.setShaderInput('time', 0)
        render.setShaderInput("eyePositionW", Vec4(base.camera.getX(),base.camera.getY(),base.camera.getZ(),0.0));
        self.setSkyBox()

        #initialize traverser
        self.picker = CollisionTraverser()
        #initialize handler
        self.queue = CollisionHandlerQueue()
        #waiting for the left mouse click
        #self.parent.Accept("mouse1", self.collisionCheck)

        self.loadPicker()
        self.raining = False
        self.raintime = 0
        self.nextraintime = 0
        splash.destroy()

        #self.pushWater(0,0,1,0.25)

    def loadPicker(self):
        #attach a CollisionRay node to the camera
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        #self.pickerNP.show()

        #add collision node (fromObject) to the traverser
        self.picker.addCollider(self.pickerNP, self.queue)
        #self.picker.showCollisions(render)

    def collisionCheck(self):
        if base.mouseWatcherNode.hasMouse():
            if base.mouseWatcherNode.isButtonDown(MouseButton.one()):
                #get the mouse position
                mpos = base.mouseWatcherNode.getMouse()
                #aim the collision ray
                self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
                #fire the ray and record, in the queue, any collisions
                self.picker.traverse(render)

                if self.queue.getNumEntries() > 0:
                    if self.queue.getNumEntries() == 1:
                        entry = self.queue.getEntry(0)
                        point = entry.getSurfacePoint(entry.getIntoNodePath())
                        px = point[0]
                        py = point[1]
                        if px >= -PSIZE/2 and px <= PSIZE/2 and py >= -PSIZE/2 and py <= PSIZE/2:
                            x,y = self.getTexturePos(px,py)
                            self.pushWater(x,y,1,0.3)
                            return True
        else:
            return False

    def getTexturePos(self, px,py):
        x = int((px + PSIZE/2) / PSIZE * SIZE)
        y = int((py + PSIZE/2) / PSIZE * SIZE)
        return x,y

    def getWaterLevel(self, pos):
        x,y = self.getTexturePos(pos[0],pos[1])
        r = self.screenImageNew.getRed(x,y)
        #print pos[0],pos[1],x,y,r
        return (r-0.5) * self.att_gridratio.vec[3].v

    def timer(self, task):
        base.graphicsEngine.extractTextureData(self.tex1, base.win.getGsg())
        self.texturechanged = False
        if self.boat != None:
#            if self.boatstopped:
            if True:
                self.screenImageNew = PNMImage(SIZE,SIZE)
                self.tex1.store(self.screenImageNew)
                # look up the water level
                pos = self.boathl.getPos(render)
                hl = self.getWaterLevel(pos)
                pos = self.boathr.getPos(render)
                hr  = self.getWaterLevel(pos)
                pos = self.boattl.getPos(render)
                tl  = self.getWaterLevel(pos)
                pos = self.boattr.getPos(render)
                tr  = self.getWaterLevel(pos)
                angle1 = math.asin(((hl+hr)/2 - (tl+tr)/2) / self.boatlength) / math.pi * 180
                angle2 = math.asin(((hl+tl)/2 - (hr+tr)/2) / self.boatwidth) / math.pi * 180
                Z = (hl+hr+tl+tr)/4 + self.BOATLEVEL

            if not self.boatstopped:
                pos = self.boattail.getPos(render)
                x,y = self.getTexturePos(pos[0],pos[1])
                self.pushWater(x,y,0,0.3)
                pos = self.boathead.getPos(render)
                x,y = self.getTexturePos(pos[0],pos[1])
                self.pushWater(x,y,0,0.4)
                angle2 += 8
                angle1 += -5
                #Z = self.BOATLEVEL

            hpr = self.boat.getHpr()
            rate = 0.1
            angle2 = hpr[1] + (angle2 - hpr[1]) * rate
            angle1 = hpr[2] + (angle1 - hpr[2]) * rate
            z = self.boat.getZ()
            Z = z + (Z - z) * rate
            self.boat.setZ(Z)
            self.boat.setHpr(0, angle2, angle1)

        self.collisionCheck()
        if self.raining:
            if task.time - self.raintime > self.nextraintime:
                    self.randomRainDrop()
                    self.raintime = task.time
                    self.nextraintime = random() * 1.5 + 0.5

        self.tex3.load(self.screenImage)
        self.tex1.store(self.screenImage)
        if self.screenImageNew != None and self.texturechanged:
            self.tex2.load(self.screenImageNew)
        else:
            self.tex2.load(self.screenImage)
        self.screenImageNew = None
        self.tex2.setWrapU(Texture.WMClamp)
        self.tex2.setWrapV(Texture.WMClamp)
        self.tex3.setWrapU(Texture.WMClamp)
        self.tex3.setWrapV(Texture.WMClamp)

        render.setShaderInput('time', task.time)
        render.setShaderInput("eyePositionW", Vec4(base.camera.getX(),base.camera.getY(),base.camera.getZ(),0.0));

        return task.cont

    def LoadLights(self):
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 0.99, 0.96, 0.5, 1 ), Vec3(-0,-0,30),
                attenuation=Vec3( 0.1, 0.03, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                fBulb=False)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setNotifier(self.setSimParam)
        #self.att_directionalLight = demobase.Att_directionalLightNode(False,"Light:Directional Light",Vec4( .9, .8, .9, 1 ) ,Vec3( 0, 8, -2.5 ) )
        #self.att_directionalLight.setLight(render)


    def LoadTerrain(self):
        self.terrain = GeoMipTerrain("terrain")
        #self.terrain.setHeightfield(Filename('demo_terrain/models/land01-map.png'))
        self.terrain.setHeightfield(Filename('demo_nature/textures/ground.tga'))
        root = self.terrain.getRoot()

        # Set terrain properties
        self.terrain.setBlockSize(32)
        self.terrain.setFactor(100)
        self.terrain.setFocalPoint(base.camera)

        root.reparentTo(render)
        #root.setSz(5)    # z (up) scale
        #minb, maxb = root.getTightBounds()
        #print minb,maxb
        #x = (minb[0]+maxb[0])/2
        #y =(minb[1]+maxb[1])/2
        root.setPos(-32,-32,-10)
        root.setScale(1,1,20)

        # Generate it.
        self.terrain.generate()

        root.clearTexture()
        ts = TextureStage('ts')
        tex = loader.loadTexture('demo_nature/textures/groundColor.tga')
        root.setTexture(ts, tex)
        self.terrain.update()

    def LoadModels(self):
        self.boat = None

        skybox1 = self.LoadSkyBox('models/angmap26/skybox.egg',  scale=(500,500,200))
        #skybox2 = self.LoadSkyBox('models/skyboxtemplate/skybox.egg')
        skybox3 = self.LoadSkyBox('models/morningbox/morningbox.egg',  scale=(500,500,200))
        self.skyboxes = [skybox1, skybox3]
        self.skyboxselection = 0
        #base.cam.node().getLens( ).setNear( 1 )
        #base.cam.node().getLens( ).setFar( 300 )

        self.att_acceleration = demobase.Att_FloatRange(False, "Water:Acceleration", 0.0, 60, 30, 1)
        self.att_dampening = demobase.Att_FloatRange(False, "Water:Dampening", 0.5, 1.0, 0.99, 3)
        self.att_gridratio = demobase.Att_Vecs(False,"Water:Grid Ratio",4,Vec4(10,10,15,5),1,20)
        self.att_reflectivity = demobase.Att_FloatRange(False, "Water:Reflectivity", 0.0, 1, 0.7, 2)
        self.att_shinning = demobase.Att_FloatRange(False, "Water:Shinning", 0.0, 1, 0.5, 2)
        self.att_watercolor = demobase.Att_color(False, "Water:Color", Vec4(0,0.25,0.5,1))

        self.att_acceleration.setNotifier(self.setSimParam)
        self.att_dampening.setNotifier(self.setSimParam)
        self.att_gridratio.setNotifier(self.setSimParam)
        self.att_reflectivity.setNotifier(self.setSimParam)
        self.att_shinning.setNotifier(self.setSimParam)
        self.att_watercolor.setNotifier(self.setSimParam)

        self.LoadTerrain()

    def setSkyBox(self):
        for skybox in self.skyboxes:
            skybox.hide()
        #self.skyboxes[self.skyboxselection].setZ(-100)
        self.skyboxes[self.skyboxselection].show()
        cubemapfile = 'tmp/cube%s_#.jpg' % self.skyboxselection
        #cubemapfile = 'tmp/cube_map#.png'
        pos = base.camera.getPos()
        hpr  = base.camera.getHpr()
        #self.actor.show()
        base.camera.setPosHpr(0,0,0,0,0,0)
        base.saveCubeMap(cubemapfile, size = 512)
        base.camera.setPos(pos)
        base.camera.setHpr(hpr)
        self.setCubeMap(cubemapfile)


    def setCubeMap(self, cubemapfile):
        tex = loader.loadCubeMap(cubemapfile)
        tex.setMinfilter( Texture.FTLinearMipmapLinear ) # for reflection blur to work
        #tex.setMagfilter( Texture.FTLinearMipmapLinear )
        self.waterplane.setShaderInput('texcube',tex)

    def ClearScene(self):
        if not self.load:
            return
        self.pickerNP.removeNode()

        taskMgr.remove('mytimer')

        self.Reset()
        self.filter.Destroy()
        self.waterplane.clearShader()

        #base.graphicsEngine.removeWindow(self.buffer2)
        #self.buffer2 = None
        self.textnode.removeNode()
        #self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def Reset(self):
        # clear other animation effects
        if hasattr(self, "interval"):
            self.interval.pause()
        ShaderPool.releaseAllShaders()
        render.setRenderModeFilled()

    def setupWaterPlane(self):
        self.filter = psFilter.psFilter1(SIZE)
        self.filter.buffer.setClearColor( Vec4( 0.5, 0.5, 0.5, 0 ) )
        self.tex1 = self.filter.buffer.getTexture()
        #print self.tex1.getFormat()
        #self.tex1.setMinfilter(Texture.FTLinear)
        #self.tex1.setFormat(Texture.FRgba32)
        #print self.tex1.getFormat()

        self.tex2 = Texture()
        self.tex3 = Texture()

        self.screenImage = PNMImage(SIZE,SIZE)
        self.screenImage.fill(0.5,0.5,0.5)
        self.tex2.load(self.screenImage)
        self.tex3.load(self.screenImage)
        self.tex1.load(self.screenImage)

        self.screenImageNew = None

        self.filter.quad.setShaderInput('tex0', self.tex2)
        self.filter.quad.setShaderInput('tex1', self.tex3)
        self.texd = loader.loadTexture("textures/dampening.tga") # for dampening purpose
        self.filter.quad.setShaderInput('dampening', self.texd)

        myShader = loader.loadShader("shaders/watersimulator_new.sha")
        self.filter.quad.setShader(myShader)

        # filter is setup, now create the water plane
        filename = "tmp/plane_%d_%d_%d_%d.egg" % (50,50,SIZE,SIZE)
        fn = Filename(filename)
        if fn.exists():
            self.waterplane = loader.loadModel(fn)
        else:
            self.waterplane = geomutil.makeEggPlane(50,50,SIZE,SIZE, filename)
        self.waterplane.setTransparency(TransparencyAttrib.MAlpha )
        self.waterplane.reparentTo(render)
        self.waterplane.setShaderInput('vtftex', self.tex2)
        myShader = loader.loadShader("shaders/vertextexture2_new.sha")
        self.waterplane.setShader(myShader)

        self.setSimParam(None)

        cNode = CollisionNode('water')
        cNode.addSolid(CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0))))
        self.waterplane.attachNewNode(cNode)

    def setSimParam(self, object):
        self.filter.quad.setShaderInput("param1", SIZE, SIZE, self.att_acceleration.v, self.att_dampening.v)
        self.waterplane.setShaderInput("gridratio", self.att_gridratio.getValue())
        self.waterplane.setShaderInput("param2", self.att_reflectivity.v, self.att_shinning.v,0,0)
        self.waterplane.setShaderInput("watercolor", self.att_watercolor.getColor())
        pos = self.att_pointLight.att_position.getValue()
        self.waterplane.setShaderInput("lightpos", pos[0],pos[1],pos[2],0)

    def Demo01(self):
        """Toggle skybox"""
        self.skyboxselection = ( self.skyboxselection + 1 ) % len(self.skyboxes)
        self.setSkyBox()

    def Demo02(self):
        """Wired frame mode"""
        self.waterplane.setRenderModeWireframe()

    def Demo03(self):
        """Filled mode"""
        self.waterplane.setRenderModeFilled()

    def Demo12(self):
        """Raining"""
        self.raining = True

    def Demo13(self):
        """Stop raining"""
        self.raining = False

    def Demo20(self):
        """Toggle Boat Simulation"""
        if self.boat != None:
            self.pivot.removeNode()
            self.boat = None
            return
        self.boat=loader.loadModel("models/boat4.egg")
        self.boat.setScale(0.15)
        self.boat.setHpr(90,0,0)
        self.boat.flattenStrong()
        min, max = self.boat.getTightBounds()
        leng = (max[0]-min[0])
        width = (max[1]-min[1])
        self.boattail = self.boat.attachNewNode("tail")
        self.boattail.setPos((-leng/2) * 0.75,0,0)
        self.boathead = self.boat.attachNewNode("head")
        self.boathead.setPos((leng/2) * 0.9,0,0)

        self.boathl = self.boat.attachNewNode("hl")
        self.boathl.setPos((leng/2), width/2,0)
        self.boathr = self.boat.attachNewNode("hr")
        self.boathr.setPos((leng/2), -width/2,0)
        self.boattl = self.boat.attachNewNode("tl")
        self.boattl.setPos((-leng/2), width/2,0)
        self.boattr = self.boat.attachNewNode("tr")
        self.boattr.setPos((-leng/2), -width/2,0)
        self.boatlength = leng
        self.boatwidth = width

        self.pivot = render.attachNewNode("boatpivot")
        self.pivot.setPos(0,0,0)
        self.pivotinterval = self.pivot.hprInterval(5,Point3(-360,0,0))
        self.pivotinterval.loop()
        self.boat.setPos(0,PSIZE/3, self.BOATLEVEL)
        self.boat.reparentTo(self.pivot)
        self.boatstopped = False


    def Demo21(self):
        """Toggle boat engine"""
        if self.boat != None:
            self.boatstopped = not self.boatstopped
            if self.boatstopped:
                self.pivotinterval.pause()
                self.boat.setHpr(0,0,0)
            else:
                self.boat.setHpr(0,5,-5)
                self.pivotinterval.resume()

    def randomRainDrop(self):
        x1 = randint(SIZE/5,SIZE*4/5)
        y1 = randint(SIZE/5,SIZE*4/5)
        v = random()*0.25 + 0.05
        r = randint(0,3)
        self.pushWater(x1,y1,r,v)


##    def pushWater(self,x1,y1,r,v):
##        if self.screenImageNew == None:
##            self.screenImageNew = PNMImage(SIZE,SIZE)
##            base.graphicsEngine.extractTextureData(self.tex1, base.win.getGsg())
##            self.tex1.store(self.screenImageNew)
##        for x in range(x1-r,x1+r+1):
##            for y in range(y1-r,y1+r+1):
##                self.screenImageNew.setRed(x,y,v)
##        self.texturechanged = True


    def pushWater(self,x1,y1,r,v):
        if self.screenImageNew == None:
            self.screenImageNew = PNMImage(SIZE,SIZE)
            base.graphicsEngine.extractTextureData(self.tex1, base.win.getGsg())
            self.tex1.store(self.screenImageNew)
        frx = max(0,x1-r)
        tox = min(SIZE,x1+r+1)
        fry = max(0,y1-r)
        toy = min(SIZE,y1+r+1)
        for x in range(frx,tox):
            for y in range(fry,toy):
                self.screenImageNew.setRed(x,y,v)
        self.texturechanged = True
