import demobase
from pandac.PandaModules import NodePath,DirectionalLight,Camera,Vec3,Vec4
from direct.actor.Actor import Actor

class SplitScreenDemo(demobase.DemoBase):
    """
    Camera - Split Screen
    Multiple display regions.
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def InitScene(self):
        base.setBackgroundColor(0.3, 0.3, 0.3)
        base.disableMouse()
        self.splitScreen(self.displayRegion1(), self.displayRegion2())

    def displayRegion1(self):
        base.camera.setPos(0, -10, 5)
        self.actor= Actor('panda.egg', {'walk' : 'panda-walk.egg'})
        self.actor.setScale(0.25,0.25,0.25)
        self.actor.reparentTo(render)
        self.actor.loop("walk")
        base.camera.lookAt(self.actor.getPos())

        #dlight = NodePath(DirectionalLight('dlight'))
        #dlight.reparentTo(base.cam)
        #render.setLight(dlight)
        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light",
            Vec4(1, 1, 1, 1 ),  Vec3( 0, 1, 0), node=base.cam)
        self.att_directionalLight.setLight(render)

        return base.cam

    def displayRegion2(self):
        dr2 = base.win.makeDisplayRegion(0.1, 0.4, 0.2, 0.6)
        self.dr2 = dr2

        self.render2 = NodePath('render2')
        cam2 = self.render2.attachNewNode(Camera('cam2'))
        dr2.setCamera(cam2)

        env = loader.loadModel('environment.egg')
        env.reparentTo(self.render2)

        cam2.setPos(-22.5, -387.3, 58.1999)

        self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .4, 1 ), node=self.render2)
        self.att_ambinentLight.setLight(self.render2)
        return cam2

    def splitScreen(self, cam, cam2):
        dr = cam.node().getDisplayRegion(0)
        dr2 = cam2.node().getDisplayRegion(0)

        #print dr.getDimensions()
        dr.setDimensions(0, 0.5, 0, 1)
        dr2.setDimensions(0.5, 1, 0, 1)

        cam.node().getLens().setAspectRatio(float(dr.getPixelWidth()) / float(dr.getPixelHeight()))
        cam2.node().getLens().setAspectRatio(float(dr2.getPixelWidth()) / float(dr2.getPixelHeight()))


    def ClearScene(self):
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)
        self.render2.removeChildren()
        self.render2.removeNode()
        dr = base.cam.node().getDisplayRegion(0)
        dr.setDimensions(0, 1, 0, 1)
        base.cam.node().getLens().setAspectRatio(float(dr.getPixelWidth()) / float(dr.getPixelHeight()))
        base.win.removeDisplayRegion(self.dr2)
