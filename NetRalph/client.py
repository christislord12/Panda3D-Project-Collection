# This started as world.py from the Panda3d Roaming Ralph demo
# though not much of the original is left. The original's credits where:

# Author: Ryan Myers
# Models: Jeff Styers, Reagan Heller
# Last Updated: 6/13/2005
#
# This tutorial provides an example of creating a character
# and having it walk around on uneven terrain, as well
# as implementing a fully rotatable camera.


# -----------------------------------------------------------------------------
# client.py 
# contains entry point for our client, main startup and 
# some "zone" management code, objects list etc.
# gsk July/August 2012


import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import WindowProperties

import random, sys, os, math, asyncore


from dynobject import DynObject, PlayerController, NetworkObjectController
from gameclient import GameClient

SPEED = 0.5

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)


class World(DirectObject):

    def __init__(self):
        
        self.d_objects = {}
        self.client = None
        
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))
        #base.win.setWidth(800)

        props = WindowProperties( )
        props.setTitle( 'Panda3D/Node.js Networking Experiment' )
        base.win.requestProperties( props ) 
        
        # Post the instructions
        self.title = addTitle("Roaming Ralph goes Networking")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left Arrow]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[Right Arrow]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.80, "[Up Arrow]: Run Ralph Forward")
        self.inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
        self.inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")
        self.inst8 = addInstructions(0.55, "Current connection lag:")
        
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.  
        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)

        # PlayerStartPos = self.environ.find("**/start_point").getPos()
        # print "start pos:", PlayerStartPos
        
        self.player = None
        
        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)


        # ----------------------------------------------------------------------
        # new: create DynObject to "host" a Ralph model for our player avatar
        
        # Accept the control keys for movement and rotation
        self.accept("escape", self.exitGame)
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        # taskMgr.add(self.moveCamera,"CameraMoveTask")
        taskMgr.add(self.moveObjects,"ObjectsMoveTask")

        # Game state variables
        self.isMoving = False
        
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav = CollisionTraverser()

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # Uncomment this line to see the collision rays
        #self.ralphGroundColNp.show()
        #self.camGroundColNp.show()
       
        # Uncomment this line to show a visual representation of the 
        # collisions occuring
        #self.cTrav.showCollisions(render)
        
        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

    def exitGame(self):
        if self.client != None:
            self.client.close()
            
        sys.exit(0)
        
    def addObject(self, object):
        self.d_objects[object.id] = object
    
    def getObject(self, id):
        if self.d_objects.has_key(id):
            return self.d_objects[id]
        return None

    def deleteObject(self, id):
        if self.d_objects.has_key(id):
            obj = self.d_objects[id]
            obj.destroy()
            del(self.d_objects[id])

    def moveObjects(self, task):
        for obj in self.d_objects.values():
            # print 'obj.move() for obj id=', obj.id
            obj.move()

        return task.cont
                        
    # called from gameclient on behalf of the server
    # id and position are server assigned
    def createActor(self, id, position, gameclient):
        actor = DynObject(render, id, position, gameclient)
        actor.motion_controller = NetworkObjectController(actor)
        self.addObject(actor)

        text = TextNode('node name_'+str(id))
        text.setText('Ralph_'+str(id))
        textNodePath = actor.actor.attachNewNode(text)
        textNodePath.setScale(1.0)        
        textNodePath.setBillboardPointEye()
        textNodePath.setZ(8.0)
        # textNodePath.setX(2.0)

        return actor

    # called by gameclient on behalf of the server. The actor passed in here
    # has been created by calling createActor() first 
    def createPlayer(self, actor):
        self.player = actor
        self.player.is_player = True
        self.player.motion_controller = PlayerController(actor)    
        
        self.accept("arrow_left", self.player.motion_controller.setKey, ["left",1])
        self.accept("arrow_right", self.player.motion_controller.setKey, ["right",1])
        self.accept("arrow_up", self.player.motion_controller.setKey, ["forward",1])
        self.accept("arrow_left-up", self.player.motion_controller.setKey, ["left",0])
        self.accept("arrow_right-up", self.player.motion_controller.setKey, ["right",0])
        self.accept("arrow_up-up", self.player.motion_controller.setKey, ["forward",0])

        # Set up the camera
        base.disableMouse()
        base.camera.setPos(self.player.getX(),self.player.getY()+10,2)

        
    #Records the state of the arrow keys
    # this is used for camera control
    def setKey(self, key, value):
        self.keyMap[key] = value

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    # this is called from the player avatar's move() 
    def moveCamera(self):

        if self.player == None: return task.cont
        
        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.
        base.camera.lookAt(self.player.actor)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())
        
        # If the camera is too far from player, move it closer.
        # If the camera is too close to player, move it farther.
        camvec = self.player.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Now check for collisions.
        self.cTrav.traverse(render)

        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.player.getZ() + 2.0):
            base.camera.setZ(self.player.getZ() + 2.0)
            
        # The camera should look in player's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above player's head.
        self.floater.setPos(self.player.getPos())
        self.floater.setZ(self.player.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return



# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------

print 'starting client v0.0.3'
w = World()
client = GameClient(w)

# client.connect('ec2-54-247-93-97.eu-west-1.compute.amazonaws.com', 8124)
client.connect('localhost', 8124)

while(True):
    taskMgr.step();
    asyncore.loop(count=1)
    
    

