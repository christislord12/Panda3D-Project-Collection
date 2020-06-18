# Author: Gsk
#
# based partially on "Roaming Ralph" and the "Nature Demo" from the panda forums
# Models: Gsk, Jeff Styers, Reagan Heller
#
# Last Updated: 7/2/2008
#
# this example program demonstrates
# - GeoMipTerrain (height map and alpha maps made in L3DT)
# - alpha splatted terrain with lighting using a shader
# - fragment shader based clipping (used to clip away terrain below the water surface)
# - shader based water with reflection, refraction and animated distortion
# - .egg model based skybox (textures made with terragen, model made and uv textured in blender)
# 
'''
TUT: shader per specchi d'acqua in movimento, geoterrain
'''

import direct.directbase.DirectStart
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import Filename
from pandac.PandaModules import PandaNode,NodePath,Camera,TextNode
from pandac.PandaModules import Vec3,Vec4,BitMask32
from pandac.PandaModules import TextureStage
from pandac.PandaModules import TexGenAttrib
from pandac.PandaModules import GeoMipTerrain
from pandac.PandaModules import CardMaker
from pandac.PandaModules import Texture
from pandac.PandaModules import TextureStage
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import AmbientLight
from pandac.PandaModules import DirectionalLight
from pandac.PandaModules import VBase4
from pandac.PandaModules import Vec4
from pandac.PandaModules import Point3

from pandac.PandaModules import Plane
from pandac.PandaModules import PlaneNode
from pandac.PandaModules import PStatClient
from pandac.PandaModules import CullFaceAttrib
from pandac.PandaModules import RenderState
from pandac.PandaModules import ShaderAttrib

from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

SPEED = 0.5

# Figure out what directory this program is in.
MYDIR=os.path.abspath(sys.path[0])
MYDIR=Filename.fromOsSpecific(MYDIR).getFullpath()
print('running from:'+MYDIR)

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
            pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

def addTextField(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
            pos=(-1.3, pos), align=TextNode.ALeft, scale = .05, mayChange=True)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
    
class WaterNode():
    def __init__(self, world, x1, y1, x2, y2, z):
        print('setting up water plane at z='+str(z))
        
        # Water surface
        maker = CardMaker( 'water' )
        maker.setFrame( x1, x2, y1, y2 )

        world.waterNP = render.attachNewNode(maker.generate())
        world.waterNP.setHpr(0,-90,0)
        world.waterNP.setPos(0,0,z)
        world.waterNP.setTransparency(TransparencyAttrib.MAlpha )
        world.waterNP.setShader(loader.loadShader( 'shaders/water.sha' ))
        world.waterNP.setShaderInput('wateranim', Vec4( 0.03, -0.015, 64.0, 0 )) # vx, vy, scale, skip
        # offset, strength, refraction factor (0=perfect mirror, 1=total refraction), refractivity
        world.waterNP.setShaderInput('waterdistort', Vec4( 0.4, 4.0, 0.4, 0.45 ))    

        # Reflection plane
        world.waterPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z ) )
        
        planeNode = PlaneNode( 'waterPlane' )
        planeNode.setPlane( world.waterPlane )
        
        # Buffer and reflection camera
        buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
        buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )

        cfa = CullFaceAttrib.makeReverse( )
        rs = RenderState.make(cfa)

        world.watercamNP = base.makeCamera( buffer )
        world.watercamNP.reparentTo(render)
        
        sa = ShaderAttrib.make()
        sa = sa.setShader(loader.loadShader('shaders/splut3Clipped.sha') )

        cam = world.watercamNP.node()
        cam.getLens( ).setFov( base.camLens.getFov( ) )
        cam.getLens().setNear(1)
        cam.getLens().setFar(5000)
        cam.setInitialState( rs )
        cam.setTagStateKey('Clipped')
        cam.setTagState('True', RenderState.make(sa)) 


        # ---- water textures ---------------------------------------------

        # reflection texture, created in realtime by the 'water camera'
        tex0 = buffer.getTexture( )
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        ts0 = TextureStage( 'reflection' )
        world.waterNP.setTexture( ts0, tex0 ) 

        # distortion texture
        tex1 = loader.loadTexture('textures/water.png')
        ts1 = TextureStage('distortion')
        world.waterNP.setTexture(ts1, tex1)
        
        
class myGeoMipTerrain(GeoMipTerrain):
    def __init__(self, name):
        GeoMipTerrain.__init__(self, name)
        
    def update(self, dummy):
        GeoMipTerrain.update(self)
        
    def setMonoTexture(self):
        root = self.getRoot()
        ts = TextureStage('ts')
        tex = loader.loadTexture('textures/land01_tx_512.png')
        root.setTexture(ts, tex)
        
    def setMultiTexture(self):
        root = self.getRoot()
        # root.setShader(loader.loadShader('shaders/splut3.sha'))
        root.setShaderInput('tscale', Vec4(16.0, 16.0, 16.0, 1.0))    # texture scaling

        tex1 = loader.loadTexture('textures/grass_ground2.jpg')
        #tex1.setMinfilter(Texture.FTLinearMipmapLinear)
        tex1.setMinfilter(Texture.FTNearestMipmapLinear)
        tex1.setMagfilter(Texture.FTLinear)
        tex2 = loader.loadTexture('textures/rock_02.jpg')
        tex2.setMinfilter(Texture.FTNearestMipmapLinear)
        tex2.setMagfilter(Texture.FTLinear)
        tex3 = loader.loadTexture('textures/sable_et_gravier.jpg')
        tex3.setMinfilter(Texture.FTNearestMipmapLinear)
        tex3.setMagfilter(Texture.FTLinear)

        alp1 = loader.loadTexture('textures/land01_Alpha_1.png')
        alp2 = loader.loadTexture('textures/land01_Alpha_2.png')
        alp3 = loader.loadTexture('textures/land01_Alpha_3.png')

        ts = TextureStage('tex1')    # stage 0
        root.setTexture(ts, tex1)        
        ts = TextureStage('tex2')    # stage 1
        root.setTexture(ts, tex2)
        ts = TextureStage('tex3')    # stage 2
        root.setTexture(ts, tex3)

        ts = TextureStage('alp1')    # stage 3
        root.setTexture(ts, alp1)
        ts = TextureStage('alp2')    # stage 4
        root.setTexture(ts, alp2)
        ts = TextureStage('alp3')    # stage 5
        root.setTexture(ts, alp3)

        # enable use of the two separate tagged render states for our two cameras
        root.setTag( 'Normal', 'True' ) 
        root.setTag( 'Clipped', 'True' ) 

        
class World(DirectObject):

    def setMouseBtn(self, btn, value):
        self.mousebtn[btn] = value

    def _setup_camera(self):
        
        sa = ShaderAttrib.make( )
        sa = sa.setShader(loader.loadShader('shaders/splut3Normal.sha'))
        
        cam = base.cam.node()
        cam.getLens().setNear(1)
        cam.getLens().setFar(5000)
        cam.setTagStateKey('Normal') 
        cam.setTagState('True', RenderState.make(sa)) 

    def __init__(self):
        
        # some constants
        self._water_level = Vec4(0.0, 0.0, 12.0, 1.0)
       
        print(str(base.win.getGsg().getMaxTextureStages()) + ' texture stages available')
        base.setFrameRateMeter(True)
        # PStatClient.connect()
        
        self.keyMap = \
        {"left":0, "right":0, "forward":0, "cam-left":0, \
         "cam-right":0, "cam-up":0, "cam-down":0, "mouse":0 }
        
        base.win.setClearColor(Vec4(0,0,0,1))
                
        # Post the instructions
        self.title = addTitle("Panda3D Tutorial: Yet Another Roaming Ralph (Walking on uneven terrain too)")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[a]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[d]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.80, "[s]: Run Ralph Forward")
        self.inst4 = addInstructions(0.70, "[Left Button]: move camera forwards")
        self.inst4 = addInstructions(0.65, "[Right Button]: move camera backwards")
        self.loc_text = addTextField(0.45, "[LOC]: ")
        
        # -------------------------------------------------------------------
        # Set up the environment
        
        # GeoMipTerrain
        self.terrain = myGeoMipTerrain('terrain')
        self.terrain.setHeightfield(Filename('models/land01-map.png'))

        # Set terrain properties
        self.terrain.setBlockSize(32)
        self.terrain.setFactor(100)
        self.terrain.setFocalPoint(base.camera)

        # Store the root NodePath for convenience
        root = self.terrain.getRoot()
        root.reparentTo(render)
        root.setSz(30)    # z (up) scale

        # Generate it.
        self.terrain.generate()

        # texture
        # self.terrain.setMonoTexture()
        self.terrain.setMultiTexture()      
        self.environ = self.terrain    # make available for original ralph code below
        
        # water
        self.water = WaterNode(self, 0, 0, 256, 256, self._water_level.getZ())
        
        # add some lighting
        ambient = Vec4(0.34, 0.3, 0.3, 1)
        direct = Vec4(0.74, 0.7, 0.7, 1)
        
        # ambient light
        alight = AmbientLight('alight')
        alight.setColor(ambient)
        alnp = render.attachNewNode(alight)
        render.setLight(alnp)
        
        # directional ("the sun")
        dlight = DirectionalLight('dlight')
        dlight.setColor(direct)
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(0.7,0.2,-0.2)
        render.setLight(dlnp)
                            
        # make waterlevel and lights available to the terrain shader
        root.setShaderInput('lightvec', Vec4(0.7, 0.2, -0.2, 1))
        root.setShaderInput('lightcolor', direct)
        root.setShaderInput('ambientlight', ambient)
        wl=self._water_level
        wl.setZ(wl.getZ()-0.05)    # add some leeway (gets rid of some mirroring artifacts)
        root.setShaderInput('waterlevel', self._water_level)    
                        
        # skybox
        self.skybox = loader.loadModel('models/skybox.egg')
        # make big enough to cover whole terrain, else there'll be problems with the water reflections
        self.skybox.setScale(500)
        self.skybox.setBin('background', 1)
        self.skybox.setDepthWrite(0)
        self.skybox.setLightOff()
        self.skybox.reparentTo(render)
        

        # Create the main character, Ralph

        # ralphStartPos = self.environ.find("**/start_point").getPos()
        ralphStartPosX = 100
        ralphStartPosY = 100        
        ralphStartPosZ = self.terrain.getElevation(ralphStartPosX, ralphStartPosY) * root.getSz()
        
        self.ralph = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        self.ralph.setPos(ralphStartPosX, ralphStartPosY, ralphStartPosZ)

        self.skybox.setPos(ralphStartPosX, ralphStartPosY, ralphStartPosZ)

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Set the current viewing target for the mouse based controls
        self.focus = Vec3(ralphStartPosX, ralphStartPosY+10, ralphStartPosZ+2)
        self.heading = 180
        self.pitch = 0
        self.mousex = 0
        self.mousey = 0
        self.last = 0
        self.mousebtn = [0,0,0]

        # Accept the control keys for movement and rotation

        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["cam-left",1])
        self.accept("arrow_right", self.setKey, ["cam-right",1])
        self.accept("arrow_up", self.setKey, ["cam-up",1])
        self.accept("arrow_down", self.setKey, ["cam-down",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        
        self.accept("arrow_left-up", self.setKey, ["cam-left",0])
        self.accept("arrow_right-up", self.setKey, ["cam-right",0])
        self.accept("arrow_up-up", self.setKey, ["cam-up",0])
        self.accept("arrow_down-up", self.setKey, ["cam-down",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])

        # mouse controls
        self.accept("mouse1", self.setMouseBtn, [0, 1])
        self.accept("mouse1-up", self.setMouseBtn, [0, 0])
        self.accept("mouse2", self.setMouseBtn, [1, 1])
        self.accept("mouse2-up", self.setMouseBtn, [1, 0])
        self.accept("mouse3", self.setMouseBtn, [2, 1])
        self.accept("mouse3-up", self.setMouseBtn, [2, 0])

        # ---- tasks -------------------------------------
        # ralph movement
        taskMgr.add(self.move,"moveTask")
        # Add a task to keep updating the terrain
        taskMgr.add(self.terrain.update, "update")
        # mouse camera movement
        taskMgr.add(self.controlCamera, "camera-task")

        # Game state variables
        self.prevtime = 0
        self.isMoving = False

        # disable std. mouse
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        # Set up the camera
        self._setup_camera()
        base.camera.setPos(self.ralph.getX(), self.ralph.getY()+10, 2)
        
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

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
        # self.ralphGroundColNp.show()
        # self.camGroundColNp.show()
       
        #Uncomment this line to show a visual representation of the 
        #collisions occuring
        # self.cTrav.showCollisions(render)
       

    
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
    

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        elapsed = task.time - self.prevtime

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.ralph)
        camright = base.camera.getNetTransform().getMat().getRow3(0)
        camright.normalize()
        if (self.keyMap["cam-left"]!=0):
            base.camera.setPos(base.camera.getPos() - camright*(elapsed*20))
        if (self.keyMap["cam-right"]!=0):
            base.camera.setPos(base.camera.getPos() + camright*(elapsed*20))
        if (self.keyMap["cam-up"]!=0):
            base.camera.setZ(base.camera.getZ() + elapsed*10)
        if (self.keyMap["cam-down"]!=0):
            base.camera.setZ(base.camera.getZ() - elapsed*10)

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.

        if (self.keyMap["left"]!=0):
            self.ralph.setH(self.ralph.getH() + elapsed*300)
        if (self.keyMap["right"]!=0):
            self.ralph.setH(self.ralph.getH() - elapsed*300)
        if (self.keyMap["forward"]!=0):
            backward = self.ralph.getNetTransform().getMat().getRow3(1)
            backward.setZ(0)
            backward.normalize()
            self.ralph.setPos(self.ralph.getPos() - backward*(elapsed*5))

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk",5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
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
        '''
        self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)
        '''
        
        # just use terrain height
        x = self.ralph.getX()
        y = self.ralph.getY()
        self.ralph.setZ(self.terrain.getElevation(x,y)*self.terrain.getRoot().getSz())
        
        # loc output
        self.loc_text.setText('[LOC] : %03.2f, %03.2f,%03.2f ' % \
                              ( self.ralph.getX(), self.ralph.getY(), self.ralph.getZ() ) )
        
        
        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.
        
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+.1)
        if (base.camera.getZ() < self.ralph.getZ() + .5):
            base.camera.setZ(self.ralph.getZ() + .5)
        # if (base.camera.getZ() > self.ralph.getZ() + 2.0):
            # base.camera.setZ(self.ralph.getZ() + 2.0)
            
        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        
        self.floater.setPos(self.ralph.getPos())
        self.floater.setZ(self.ralph.getZ() + 2.0)
        base.camera.lookAt(self.floater)
               
        # Store the task time and continue.
        self.prevtime = task.time
        return Task.cont

    # mouse controled main camera
    def controlCamera(self, task):
        # figure out how much the mouse has moved (in pixels)
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, 100, 100):
            self.heading = self.heading - (x - 100)*0.2
            self.pitch = self.pitch - (y - 100)*0.2
        if (self.pitch < -89): self.pitch = -89
        if (self.pitch >  89): self.pitch =  89
        base.camera.setHpr(self.heading,self.pitch,0)
        dir = base.camera.getMat().getRow3(1)
        elapsed = task.time - self.last
        if (self.last == 0): elapsed = 0
        if (self.mousebtn[0]):
            self.focus = self.focus + dir * elapsed*30
        if (self.mousebtn[1]) or (self.mousebtn[2]):
            self.focus = self.focus - dir * elapsed*30
        base.camera.setPos(self.focus - (dir*5))

        # Time for water distortions
        render.setShaderInput('time', task.time)

        # move the skybox with the camera
        campos = base.camera.getPos()
        self.skybox.setPos(campos)

        # update matrix of the reflection camera
        mc = base.camera.getMat( )
        mf = self.waterPlane.getReflectionMat( )
        self.watercamNP.setMat(mc * mf)

        self.focus = base.camera.getPos() + (dir*5)
        self.last = task.time
        return Task.cont

print('instancing world...')
w = World()

print('calling run()...')
run()

