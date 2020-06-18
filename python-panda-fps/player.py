from pandac.PandaModules import *
from panda3d.core import *
from direct.actor.Actor import Actor
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText

import bullet

class Player(object):
    """
        Player is the main actor in the fps game
    """
    speed = 50
    FORWARD = Vec3(0,2,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)
    walk = STOP
    strafe = STOP
    readyToJump = False
    jump = 0
    jet = False
    hover = False
    thirdPerson = False
    fallRate = 2
    gravForce = 0.1
    jumpForce = 2
    jetForce = 4
    eyeLevel = 0.1
    position = None
    
    ID = 0
    
    # States for networking
    moveState = None
    turnState = None
    
    def __init__(self, game = None, Local = True, Client = None, ID = 0):
        """ inits the player """
        self.Local = Local
        self.Client = Client
        self.game = game
        self.ID = ID
        
        self.loadModel()
        if Local:
            self.setUpCamera()
            self.attachControls()
            taskMgr.add(self.mouseUpdate, 'mouse-task')
            taskMgr.add(self.moveSky, 'sky-task')
            taskMgr.add(self.showPos, 'position-task')
        else:
            self.attachClient(Client)
            
        
        
        if base.isClient:
            taskMgr.add(self.xmitPos, 'transmit-task')
        #else:
        self.createCollisions()
        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.jumpUpdate, 'jump-task')
        
        
        
        
    def loadModel(self):
        """ make the nodepath for player """
        # I have no idea what a NodePath is right now, but I know loadModel works fine
        #if self.Local:
            # These should be replaced with Actor() 's after I make or get an animated model
            #self.node = loader.loadModel("./resources/models/player")
        self.node = Actor("resources/models/thing",
                                {"walk": "resources/models/thing-walk"})
        #else:
            #self.node = loader.loadModel("./resources/models/player")
            #self.node = Actor("resoures/models/thing",
            #                    {"walk": "resources/models/thing-walk"})
        
        #body = loader.loadModel("resources/models/body")
        #head = loader.loadModel("resources/models/head")
        #head.setScale(0.7)
        #Larm = loader.loadModel("resources/models/arm")
        #Rarm = loader.loadModel("resources/models/arm")
        #Lleg = loader.loadModel("resources/models/leg")
        #Rleg = loader.loadModel("resources/models/leg")
        #
        #head.reparentTo(body)
        #head.setPos(0, 0, 2)
        #
        #Larm.reparentTo(body)
        #Larm.setPos(-1, 0, 0)
        #
        #Rarm.reparentTo(body)
        #Rarm.setPos(1, 0, 0)
        #
        #self.node = body
        #
        self.node.reparentTo(base.lightable)
        self.node.setPos(0,0,22)
        self.node.setScale(.05)
        
        self.node.loop("walk")
        
        #self.physxnode = NodePath("PhysicsNode")
        #self.physxnode.reparentTo(render)
        #self.actornode = ActorNode("cubey")
        #self.actornodeatt = self.physxnode.attachNewNode(self.actornode)
        #base.physicsMgr.attachPhysicalNode(self.actornode)
        #self.node.reparentTo(self.actornodeatt)
        
        #self.actornode.getPhysicsObject().setMass(136.077)
    
    def setUpCamera(self):
        """ puts camera at the players node """
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        base.camera.reparentTo(self.node)
        
    def createCollisions(self):
        """ create a collision solid and ray for the player """
        cn = CollisionNode('player')
        cn.addSolid(CollisionSphere(0,0,0,3))
        solid = self.node.attachNewNode(cn)
        base.cTrav.addCollider(solid,base.pusher)
        base.pusher.addCollider(solid,self.node, base.drive.node())
        
        # init players floor collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,-.2)
        ray.setDirection(0,0,-1)
        cn = CollisionNode('playerRay')
        cn.addSolid(ray)
        cn.setFromCollideMask(BitMask32.bit(0))
        cn.setIntoCollideMask(BitMask32.allOff())
        solid = self.node.attachNewNode(cn)
        self.nodeGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(solid, self.nodeGroundHandler)
        
        """downray = CollisionRay()
        downray.setOrigin(0,0,.2)
        downray.setDirection(0,0,1)
        cn = CollisionNode('playerDownRay')
        cn.addSolid(downray)
        cn.setFromCollideMask(BitMask32.bit(0))
        cn.setIntoCollideMask(BitMask32.allOff())
        solid = self.node.attachNewNode(cn)
        self.nodeCielingHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(solid, self.nodeCielingHandler)"""
        
    def attachControls(self):
        """ attach key events """
        base.accept( "space" , self.__setattr__,["readyToJump",True])
        base.accept( "space-up" , self.__setattr__,["readyToJump",False])
        base.accept( "s" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w" , self.__setattr__,["walk",self.FORWARD])
        base.accept( "s" , self.__setattr__,["walk",self.BACK] )
        base.accept( "s-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "a" , self.__setattr__,["strafe",self.LEFT])
        base.accept( "d" , self.__setattr__,["strafe",self.RIGHT] )
        base.accept( "a-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "d-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "mouse3" , self.__setattr__,["jet",True] )
        base.accept( "mouse3-up" , self.__setattr__,["jet",False] )
        
        base.accept( "mouse2" , self.__setattr__,["hover",True] )
        base.accept( "mouse2-up" , self.__setattr__,["hover",False] )
        
        base.accept( "tab" , self.toggleThird, )
        base.accept( "1" , self.node.setPos, [0, 0, 2] )
       
        base.accept( "mouse1" , self.fire )
    
    def detachControls(self):
        """ detach key events """
        base.ignore( "space" )
        base.ignore( "space-up" )
        base.ignore( "s" )
        base.ignore( "w" )
        base.ignore( "s" )
        base.ignore( "s-up" )
        base.ignore( "w-up" )
        base.ignore( "a" )
        base.ignore( "d" )
        base.ignore( "a-up" )
        base.ignore( "d-up" )
        base.ignore( "mouse3" )
        base.ignore( "mouse3-up" )
        
        base.ignore( "tab" )
        base.ignore( "1" )
    
    def showPos(self, task):
      if self.position is None: self.position = OnscreenText(text = "0", pos = (-0.5,-0.5), 
            scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
      else: self.position.setText(str(self.node.getPos()))
      return task.cont
        
    def toggleThird(self):
        if self.thirdPerson:
            self.thirdPerson = False
            base.camera.setY(0)
            base.camera.setZ(0)
        else:
            self.thirdPerson = True
            base.camera.setY(-7)
            base.camera.setZ(3)
        
    def attachClient(self, Client):
        if Client:
            self.Client = Client
            self.Client.attachPlayer(self)
        
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        if not self.game.mouseCapture: return task.cont
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
            self.node.setH(self.node.getH() -  (x - base.win.getXSize()/2)*0.1)
            newP = base.camera.getP() - (y - base.win.getYSize()/2)*0.1
            if newP > 90: newP = 90
            if newP < -90: newP = -90
            base.camera.setP(newP)
        return task.cont
    
    def moveUpdate(self,task): 
        """ this task makes the player move """
        # move where the keys set it
        self.node.setPos(self.node,self.walk*globalClock.getDt()*self.speed)
        self.node.setPos(self.node,self.strafe*globalClock.getDt()*self.speed)
        return task.cont
        
    def jumpUpdate(self,task):
        """ this task simulates gravity and makes the player jump """
        if self.hover: return task.cont
        # Jets
        if self.jet: self.jump = self.jetForce
        
        # get the highest Z from the down casting ray
        highestZ = -400
        for i in range(self.nodeGroundHandler.getNumEntries()):
            entry = self.nodeGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            #print entry.getIntoNode().getName()
            if z > highestZ and entry.getIntoNode().getName() == "Cube":
                highestZ = z
        
        # Terrain collisions
        if self.node.getX() > base.terrain.getRoot().getX() and self.node.getY() > base.terrain.getRoot().getY():
            terrainZ = base.terrain.getElevation(self.node.getX() - base.terrain.getRoot().getX(),
                                                 self.node.getY() - base.terrain.getRoot().getY())
            terrainZZ = terrainZ * 35
            if terrainZZ > highestZ and self.node.getZ() > terrainZZ: highestZ = terrainZZ
        
        """# get the lowest Z from the upward casting ray
        lowestZ = 400
        for i in range(self.nodeCielingHandler.getNumEntries()):
            entry = self.nodeCielingHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            
            if z < lowestZ and entry.getIntoNode().getName() == "Cube":
                lowestZ = z
                #print "up surface at", str(z)"""
        
        # gravity effects and jumps
        self.node.setZ(self.node.getZ()+self.jump*globalClock.getDt())
        self.jump -= self.fallRate*globalClock.getDt()
        if highestZ > self.node.getZ()-self.eyeLevel:
            self.jump = 0
            self.node.setZ(highestZ+self.eyeLevel)
            if self.readyToJump:
                self.jump = self.jumpForce
                base.jumpSound.play()
        
        """if lowestZ < self.node.getZ()+self.eyeLevel and self.jump < 0:
            #print "top collide"
            self.jump = 0
            self.node.setZ(lowestZ+self.eyeLevel)"""
        return task.cont
    
    def moveSky(self, task):
        try:
            base.sky.setX(self.node.getX())
            base.sky.setY(self.node.getY())
            base.sky.setZ(self.node.getZ())
        except AttributeError:
            #nosky
            return
        return task.cont
    
    def xmitPos(self, task):
        """ Transmits player motion and rotation in two datagrams """
        # Movement
        current = [self.walk.y, self.strafe.x, self.readyToJump, self.jet]
        if current != self.moveState: base.serverConnection.doPacket(200, "FF!!", current)
        self.moveState = current
        
        # Rotation
        current = [self.node.getH(), self.node.getP(), self.node.getR()]
        if current != self.turnState: base.serverConnection.doPacket(201, "FFF", current)
        self.turnState = current
    
        return task.cont
        
    def fire(self):
        base.bulletManager.makeBullet(self.node.getPos(), self.node.getHpr(), 0.01, 5)
        
        