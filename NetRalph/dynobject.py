from Queue import Queue

from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Vec3,Vec4,BitMask32
from direct.actor.Actor import Actor

import state

# controller objects: these are basically the "motor" components 
# for dynamic objecs (DynObj)
# required interface implementation:
# processMove()  : regular update to control movement state of the underlying DynObj
# saveNetState(pos) : queue up incoming server state data


# The PlayerController is used to for the player's avatar
# as such it must be able to react to player control input
class PlayerController():
    
    def __init__(self, dynobj):
        self.obj = dynobj
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        
    # nothing happening here right now for the player controller
    def processMove(self):
        pass
        # print 'PlayerController.doMove(), id=', self.obj.id
        # actor = self.obj.actor
        
 
    #Records the state of the arrow keys: used for player control
    def setKey(self, key, value):
        # print 'DynObj.setKey() ', key, ' ', value
        self.keyMap[key] = value

        # process the inputs that are relevant to us
        # we flag the various states using a bitfield 
        if (self.keyMap["left"]!=0):
            self.obj.state |= state.LEFT
        else:
            self.obj.state &= ~state.LEFT
            
        if (self.keyMap["right"]!=0):
            self.obj.state |= state.RIGHT
        else:
            self.obj.state &= ~state.RIGHT
            
        if (self.keyMap["forward"]!=0):
            self.obj.state |= state.FORWARD
        else:
            self.obj.state &= ~state.FORWARD
        
        print 'key=', key, ' value=', value, ' state=', self.obj.state
        
        # for now we send an update to the server whenver our control state
        # changes (i.e the player presses a movement/rotation related key)
        self.obj.client.sendClientPositionUpdate(self.obj.id, self.obj.state, self.obj.getPos(), self.obj.getH())

    # the player controller does need to process these
    def saveNetState(self, pos):
        print 'PlayerController.saveNetState(): dropping data'

# The NetworkObjectController is used to for "shadows" of server objects
# i.e all DynObj that the server controls (basically anything apart from
# the player's avatar)
# We rely on the server sending us state updates which we store and playback
class NetworkObjectController():
    
    def __init__(self, dynobj):
        self.obj = dynobj
        self.net_state_queue = Queue()
        self.target_state = None

    #  GameClient calls this in order to store incoming network state messages
    # Parameter state is a tuple [ state (int) , position (Vec3), heading (float)] 
    def saveNetState(self, state):
        self.net_state_queue.put(state)
        # print 'NetworkObjectController.saveNetState(): queue len=',  self.net_state_queue.qsize()

    # what we are doing here is absurdly primitve for now: simply read the next network state from the queue
    # (if any exists) and copy over state, position and heading. No smoothing or prediction is perfomed at all
    # while this works, it will produce increasingly ugly ghosting of objects as soon as lag increases and
    # particularly when theres noriceable changes in lag in between calls
    def processMove(self):
        # print 'NetworkObjectController.doMove()'
        actor = self.obj.actor
        
        # process the networs state queue
        if self.net_state_queue.qsize() > 0:
            print 'retrieveing next queued net state'
            self.target_state = self.net_state_queue.get()   # netstate is a tuple [Vec3, int] containing position and movement state
                         
            self.obj.state = self.target_state[0]  # copy network object's state
            net_pos = self.target_state[1]         # the original object is here : for now simply copy
            net_hdg = self.target_state[2]         # also copy heading 
                
            actor.setPos(net_pos)
            actor.setH(net_hdg)
            
            # cur_pos = Vec3(self.obj.getPos())   # we are here right now 
            # print 'new state=', self.state, 'target_pos=', net_pos, ' curpos=',  cur_pos
    
        
class DynObject():

    def __init__(self, render, objid, start_pos, gameclient):
        self.client = gameclient
        self.id = objid
        self.motion_controller = None
        self.is_player = False
        
        # state  management
        self.isAnimating = False
        self.state = state.IDLE
        
        self.render = render    # scene graph root
        
        #  create the panda3d actor: just load a default model for now
        self.actor = Actor("models/ralph",
                            {"run":"models/ralph-run",
                             "walk":"models/ralph-walk"})
                             
        self.actor.reparentTo(render)
        self.actor.setScale(.2)
        self.actor.setPos(start_pos)

        # prepare collision handling
        self.cTrav = CollisionTraverser()
        self.GroundRay = CollisionRay()
        self.GroundRay.setOrigin(0,0,1000)
        self.GroundRay.setDirection(0,0,-1)
        self.GroundCol = CollisionNode('actorRay')
        self.GroundCol.addSolid(self.GroundRay)
        self.GroundCol.setFromCollideMask(BitMask32.bit(0))
        self.GroundCol.setIntoCollideMask(BitMask32.allOff())
        self.GroundColNp = self.actor.attachNewNode(self.GroundCol)
        self.GroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.GroundColNp, self.GroundHandler)

    def destroy(self):
        if self.actor != None:
            self.actor.cleanup()
            self.actor.removeNode()
            self.actor = None
            
    # called reqularly from a Panda3 task
    # move the object according to its current state
    def move(self):
        actor = self.actor

        # save our initial position so that we can restore it,
        # in case we fall off the map or run into something.
        startpos = actor.getPos()
        
        # let the motion_controller determine our new state
        self.motion_controller.processMove()
        
        # evaluate state and  move/rotate the actor accordingly
        if (self.state & state.LEFT):
            actor.setH(actor.getH() + 300 * globalClock.getDt())
        if (self.state & state.RIGHT):
            actor.setH(actor.getH() - 300 * globalClock.getDt())
        if (self.state & state.FORWARD):
            actor.setY(actor, -25 * globalClock.getDt())

        # Simplistic animation control: 
        # If we are moving, loop the run animation.
        # If we are standing still, stop the animation.
        if (self.state != state.IDLE):
            if self.isAnimating is False:
                actor.loop("run")
                self.isAnimating = True
        else:
            if self.isAnimating:
                actor.stop()
                actor.pose("walk", 5)
                self.isAnimating = False
    
        # Now check for collisions.
        self.cTrav.traverse(render)

        # Adjust Z coordinate.  If the ray hit terrain,
        # update Z. If it hit anything else, or didn't hit anything, put
        # us back where we were last frame.
        entries = []
        for i in range(self.GroundHandler.getNumEntries()):
            entry = self.GroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.actor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.actor.setPos(startpos)

        # if this is the player avatar: make the camera follow us
        if self.is_player is True:
            self.client.world.moveCamera()

    # convenience getter/setters
    def setPos(self, pos):
        self.actor.setPos(pos)
    def getPos(self):
        return self.actor.getPos()
    def getH(self):
        return self.actor.getH()
    def getX(self):
        return self.actor.getX()
    def getY(self):
        return self.actor.getY()
    def getZ(self):
        return self.actor.getZ()
        
