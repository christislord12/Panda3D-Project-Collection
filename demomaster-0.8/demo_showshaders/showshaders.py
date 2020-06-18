from random import randint, random
import math, sys, colorsys, threading
import demobase, camerabase
from pandac.PandaModules import Vec3,Vec4,Point3, TextNode, TextureStage, NodePath, VBase4
from direct.filter.CommonFilters import CommonFilters
from direct.interval.LerpInterval import LerpFunc
####################################################################################################################
class ShowShadersDemo(demobase.DemoBase):
    """
    Shaders - Show Panda Shaders
    Shaders demos from http://panda3d.org/phpbb2/viewtopic.php?t=4791
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def SetupCamera(self):
        self.SetCameraPos(Vec3(0,0,40), Vec3(0,0,0))

    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)

        self.att_bloomsize = demobase.Att_IntRange(False, "size", 1, 3, 1)
        self.att_bloomsize.setNotifier(self.bloomchange)
        self.att_bloomintensity = demobase.Att_FloatRange(False, "intensity", 0.01, 10, 3, 2)
        self.att_bloomintensity.setNotifier(self.bloomchange)
        self.att_bloomdesat = demobase.Att_FloatRange(False, "desat", -5, 5, -0.5, 2)
        self.att_bloomdesat.setNotifier(self.bloomchange)
        self.att_bloommintrigger = demobase.Att_FloatRange(False, "mintrigger", 0, 1, 0.6, 2)
        self.att_bloommintrigger.setNotifier(self.bloomchange)
        self.att_bloommaxtrigger = demobase.Att_FloatRange(False, "maxtrigger", 0, 1, 1, 2)
        self.att_bloommaxtrigger.setNotifier(self.bloomchange)
        self.att_blend = demobase.Att_Vecs(False, "blend", 4, [1,0,0,1], 0, 1, 2)
        self.att_blend.setNotifier(self.bloomchange)

        self.textnode = render2d.attachNewNode("textnode")
        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()
        self.LoadFilter()
        #render.setShaderAuto()
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        #self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
        #             [-59,-59,5], [59,59,45], [-45,45, -17], [0,0,45], Vec3(8,-8,3), rate=0.2)
        #self.parent.Accept("escape", self.att_cameracontrol.Stop)
        #self.parent.Accept("enter", self.att_cameracontrol.Resume)
        #self.att_cameracontrol.Stop()
#        return
    	demobase.addInstructionList(-1,0.95,0.05,
"""Zoom in to check the shader information.
Use the attribute panel to control the bloom attributes""",node=self.textnode)


    def LoadLights(self):
        self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(0, 0, 0, 1 ))
        self.att_ambinentLight.setLight(render)

        plightCenter = NodePath( 'plightCenter' )
        plightCenter.setPos(0,0,10)
        plightCenter.reparentTo( render )
        self.interval = plightCenter.hprInterval(6, Vec3(360, 0, 0))
        self.interval.loop()

        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( .8, .8, .8, 1 ), Vec3(20,0,0), attenuation=Vec3( 1, 0.0, 0.0 ), node=plightCenter, fBulb=True)
        self.att_pointLight.setLight(render)

        self.att_lightbrightness = demobase.Att_Boolean(False, "Light:Changing Brightness", False)
        self.att_lightbrightness.setNotifier(self.changebrightness)
        self.interval2 = LerpFunc(self.animate, 10.0, 0.0, 360.0)
        self.interval2.pause()

    def LoadFilter(self):
        # Check video card capabilities.
        if (base.win.getGsg().getSupportsBasicShaders() == 0):
            self.addTitle("Glow Filter: Video driver reports that shaders are not supported.")
            return
        # Use class 'CommonFilters' to enable a bloom filter.
        # The brightness of a pixel is measured using a weighted average
        # of R,G,B,A.  We put all the weight on Alpha, meaning that for
        # us, the framebuffer's alpha channel alpha controls bloom.
        self.filters = CommonFilters(base.win, base.cam)
        self.bloomchange(None)

    def LoadModels(self):
        models = list()
        effects = [ 'diffuse', 'normal', 'gloss', 'glossModulate', 'glow', 'glowModulate' ]
        for x in xrange( 0, 64 ):
            mdl = loader.loadModel( 'sphere-tbn.egg' )
            mdl.setTwoSided( True )
            pX = x%8
            pY = x//8

            pos = Vec3( pX*3 - 10, pY*3 - 8, 0 )
            mdl.setPos( pos )

            s = mdl.getBounds().getRadius()
            mdl.setScale( 1./s*1.4 )

            txt = '%i/%i' % (pX, pY)

            efId = effects.index('diffuse')
            if x & 2**efId:
                tex = loader.loadTexture( 'diffusemap.png' )
                ts = TextureStage('ts')
                ts.setMode(TextureStage.MModulate)
                mdl.setTexture(tex, 1)
                txt += " diffuse"

            efId = effects.index('normal')
            if x & 2**efId:
                tex = loader.loadTexture( 'normalmap.png' )
                ts = TextureStage('ts')
                ts.setMode(TextureStage.MNormal)
                mdl.setTexture(ts, tex)
                txt += " normal"

            efId = effects.index('gloss')
            if x & 2**efId:
                tex = loader.loadTexture( 'glossmap.png' )
                ts = TextureStage('ts')
                ts.setMode(TextureStage.MGloss)
                mdl.setTexture(ts, tex)
                txt += " gloss"

            efId = effects.index('glossModulate')
            if x & 2**efId:
                tex = loader.loadTexture( 'glossmap.png' )
                ts = TextureStage('ts')
                ts.setMode(TextureStage.MModulateGloss)
                mdl.setTexture(ts, tex)
                txt += " glossMod"

            efId = effects.index('glow')
            if x & 2**efId:
                tex = loader.loadTexture( 'glowmap.png' )
                ts = TextureStage('ts')
                ts.setMode(TextureStage.MGlow)
                mdl.setTexture(ts, tex)
                txt += " glow"

            efId = effects.index('glowModulate')
            if x & 2**efId:
                tex = loader.loadTexture( 'glowmap.png' )
                ts = TextureStage('ts')
                ts.setMode(TextureStage.MModulateGlow)
                mdl.setTexture(ts, tex)
                txt += " glowMod"

            valid = True

            # it's not valid to have gloss and glossmodulate active at once
            efId1 = effects.index('gloss')
            efId2 = effects.index('glossModulate')
            if (x & 2**efId1) and (x & 2**efId2):
                valid = False
            # it's not valid to have glow and glowmodulate active at once
            efId1 = effects.index('glow')
            efId2 = effects.index('glowModulate')
            if (x & 2**efId1) and (x & 2**efId2):
                valid = False
            # dont show models with invalid texture mixings
            if valid:
                mdl.reparentTo( render )
                text = TextNode('node name')
                text.setTextColor(1, 1, 1, 1)
                text.setText(txt)
                tNode = render.attachNewNode(text)
                tNode.setPos( pos + Vec3(0,1.1,0) )
                tNode.setScale( 0.1 )
                tNode.setHpr(0,-90,0)
                tNode.setShaderOff()
                tNode.setLightOff()


    def addTitle(self, title):
    	demobase.addInstructionList(0,-0.8,0.05,title,align=TextNode.ACenter,node=self.textnode)

    def ClearScene(self):
        self.filters.cleanup()
        if hasattr(self, "interval"):
            self.interval.pause()
        if hasattr(self, "interval2"):
            self.interval2.pause()

        self.textnode.removeNode()
        #self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)


    def bloomchange(self, object):
        size = self.att_bloomsize.v
        intensity = self.att_bloomintensity.v
        desat = self.att_bloomdesat.v
        mintrigger = self.att_bloommintrigger.v
        maxtrigger = self.att_bloommaxtrigger.v
        if mintrigger >= maxtrigger:
            mintrigger = maxtrigger-0.01
        blend=(self.att_blend.vec[0].v,self.att_blend.vec[1].v,self.att_blend.vec[2].v,self.att_blend.vec[3].v)
        filterok = self.filters.setBloom(blend=blend,
                mintrigger=mintrigger, maxtrigger=maxtrigger,
                desat=desat, intensity=intensity, size=size)
        #filterok = self.filters.setBloom(blend=(1,0,0,1), desat=-0.5, intensity=3.0, size=1)
        if (filterok == False):
            self.addTitle("Shader: Video card not powerful enough to do image postprocessing")
            return

    def animate(self, t):
        radius = 4.3
        angle = math.radians(t)
        c = (math.sin(angle) + 0.5)
        cr=VBase4( c, c, c, c)
        self.att_pointLight.setColor(None, cr)
        self.att_pointLight.att_bulb.setBulbColor(None, cr)

    def changebrightness(self, object):
        if self.att_lightbrightness.v:
            self.interval2.loop()
        else:
            self.interval2.pause()
            c = 0.8
            cr=VBase4( c, c, c, c)
            self.att_pointLight.setColor(None, cr)
            self.att_pointLight.att_bulb.setBulbColor(None, cr)
