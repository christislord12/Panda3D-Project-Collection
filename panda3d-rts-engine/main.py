
import direct.directbase.DirectStart
from GuiTools import *
from CameraHandler import CameraHandler
from direct.task import Task 
from direct.actor import Actor
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject


from pandac.PandaModules import GeoMipTerrain 
from pandac.PandaModules import TextureStage 
from pandac.PandaModules import TextNode 
from pandac.PandaModules import Texture 
from pandac.PandaModules import Filename 

from panda3d.ai import *

import math 
SHADER = ""


class RTSEngine(DirectObject):
    
    def __init__(self):
        from pandac.PandaModules import loadPrcFileData
        loadPrcFileData("", "want-directtools #t")
        loadPrcFileData("", "want-tk #t")
        self.camHandler = None
        self.environ = None
        self.isMoving = False
        self.trav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        self.picked = None
        self.selected = None
        

        self.setupEnvironment()
        self.setupCamera()
        self.setupActors()
        self.setupLighting()
        self.gui = mouseSelectTool()
        self.gui.selectable = [self.box,self.box2]
        
        
   
   
    def setupAI(self):
        self.AIWorld = AIWorld(render)
        self.AIChar = AICharacter("ralph",self.ralph,60,0.5,15)
        self.AIWorld.addAiChar(self.AIChar)
        self.AIBehaviors = self.AIChar.getAiBehaviors()
        
        
        taskMgr.add(self.AIUpdate,"AIUpdate")
        
        return
    
    
   
   
    def run(self):
        run()
  
    

    def setupMouseCollision(self):
        
        
        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.trav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)
 

        
        
    def setupCamera(self):
        self.camHandler = CameraHandler()
        self.camHandler.setTarget(self.environ.getX(),self.environ.getY(),self.environ.getZ())
        
    def setupActors(self):
        # Create the main character, Ralph
        ralphStartPos = self.environ.find("**/start_point").getPos()
        
        self.ralph = Actor.Actor("models/ralph",{"run":"models/ralph-run","walk":"models/ralph-walk"})
        self.ralph =  loader.loadModel("models/ralph")
        self.ralph.setPos(ralphStartPos)
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        
        
        self.box = loader.loadModel("models/box")
        self.box.setPos(5,5,1)
        self.box.setColor(1,0,0)
        self.box.setScale(.5)
        self.box.reparentTo(render)
        
        self.box2 = loader.loadModel("models/box")
        self.box2.setPos(-10,-10,1)
        self.box2.setColor(1,1,0)
        self.box2.setScale(.5)
        self.box2.reparentTo(render)
        
        
        
    def setupLighting(self):
        #Setup the lighting and the shader to make it look cartoony
        plightnode = PointLight("point light")
        plightnode.setAttenuation(Vec3(1,0,0))
        plight = render.attachNewNode(plightnode)
        plight.setPos(30,-50,0)
        alightnode = AmbientLight("ambient light")
        alightnode.setColor(Vec4(0.8,0.8,0.8,1))
        alight = render.attachNewNode(alightnode)
        render.setLight(alight)
        render.setLight(plight)
        self.lastMousePos = None
        
        alight = AmbientLight("alight")
        alight.setColor(VBase4(0.5,0.5,0.5,0.5))
        self.alnp = self.ralph.attachNewNode(alight)
        
        
        
        
    def setupEnvironment(self):
        
        #self.environ = loader.loadModel("models/world")
        #self.terrain = GeoMipTerrain("MyTerrain")
        #self.terrain.setHeightfield(Filename("models/testHeightMap.png"))
        #self.terrain.setBruteforce(True) 
        #self.terrain.setBlockSize(64)
        #self.terrain.setNear(40)
        #self.terrain.setFar(100)
        #self.terrain.setFocalPoint(base.camera)
        #self.environ = self.terrain.getRoot()
        #self.environ.setShader(Shader.make(SHADER))
        #self.environ.setSz(50)

        #self.terrain_tex = loader.loadTexture('world/shortGrass.png')
        #self.ts = TextureStage('ts')
        #self.environ.setTexScale(self.ts.getDefault(),10,10)
        #self.environ.setTexture(self.terrain_tex,1)
        #self.terrain.generate() 
        #self.environ.reparentTo(render)
        #base.toggleWireframe()
        
        #self.environ = self.terrain.getRoot()
        #self.environ.setPos(1,1,0)
        
        
        
        self.environ = loader.loadModel("models/world") 
        self.environ.reparentTo(render)
        self.environ.setScale(0.25,0.25,0.25) 
        self.environ.setPos(0,0,0)

    def update(self, task): 
        self.terrain.setFocalPoint(base.camera.getX(),base.camera.getY()) 
        self.terrain.update()
        return task.cont
            
    def setMove(self):
        try:
            print "none"
        except:
            print "Failed"
            
        self.ralph.loop("run")
        return
        
        
        
    def AIUpdate(self,task):
        
        self.AIWorld.update()
        if(self.AIBehaviors.behaviorStatus("pathfollow") == "done"):
            self.ralph.stop("run")
            self.ralph.pose("walk",0)
           
        return task.cont
    
    
    def handleRalphCollision(self,task):
        
        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(0,0,0)

        return task.cont
    
                            
                

        



if __name__ == "__main__":
    
    rts = RTSEngine()
    
    rts.run()