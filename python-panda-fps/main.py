"""
awsd - movement
space - jump
mouse - look around
"""

import sys
from direct.gui.OnscreenText import OnscreenText
import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.gui.DirectGui import *

from gameconnection import *
from server import *
from serverconnection import *
from player import Player

import bulletManager

#from gui.test import *

class mainMenu(object):
    def __init__(self):
        self.text = OnscreenText(text = "Start game", pos = (0.95, -0.95), scale = 0.07, fg=(1,0.5,0.5,1), align = TextNode.ACenter)
        self.serverButton = DirectButton(text = ("Start as Server", "Start as Server", "Start as Server", "Start as Server"), scale = 0.05, pos = (0, 0, 0.1), command = self.startServer)
        self.ipEntry = DirectEntry(text = "", scale = 0.05, command = self.startClient, initialText="Connect IP", numLines = 1, focus=0,focusInCommand=self.clearText, pos=(0.25, 0, 0))
        self.clientButton = DirectButton(text = ("Start as Client", "Start as Client", "Start as Client", "Start as Client"), scale = 0.05, pos = (0, 0, 0), command = self.startClient)
        self.exitButton = DirectButton(text = "Exit", scale = 0.05, pos = (0, 0, -0.1), command = sys.exit)
        base.accept( "escape" , sys.exit)
    
    def clearText(self):
        self.ipEntry.enterText('')
    
    def startServer(self):
        print "Start up as server"
        self.destroyObjects()
        FPS(True)
    
    def startClient(self, ip = None):
        print "Start up as client"
        self.destroyObjects()
        #if ip is None: ip = self.ipEntry['text']
        if ip is None: ip = "127.0.0.1"
        FPS(False, ip)
    
    def destroyObjects(self):
        self.text.destroy()
        self.serverButton.destroy()
        self.ipEntry.destroy()
        self.clientButton.destroy()
        self.exitButton.destroy()

##################################################################################################

class FPS(object):
    """
        This is a very simple FPS like -
         a building block of any game i guess
    """
    
    mouseCapture = True
    
    def __init__(self, hosting = True, ip = None):
        """ create a FPS type game """
        # Decide if server or client and initialize accordingly
        if hosting:
            base.server = ServerClass(self)
            base.isClient = False
        else:
            base.serverConnection = ServerConnectionClass(self)
            base.isClient = True
        
        render.setShaderAuto()
        #base.lightable = NodePath("lightable")
        base.lightable = render.attachNewNode("lightable")
        
        self.initCollision()
        if hosting: self.initPlayer()
        self.initLighting()
        #self.initControls()
        
        # Load up the mission objects
        from missions.default import mission
        self.mission = mission()
        self.mission.load()
        
        base.accept( "escape" , sys.exit)
        base.accept( "`" , self.toggleMouse)
        
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.MRelative)
        #props.setFullscreen(True)
        base.win.requestProperties(props)
        
        
    
    def toggleMouse(self):
        props = WindowProperties()
        if self.mouseCapture:
            self.mouseCapture = False
            props.setCursorHidden(False)
        else:
            self.mouseCapture = True
            props.setCursorHidden(True)
        base.win.requestProperties(props)
    
    def initCollision(self):
        """ create the collision system """
        base.cTrav = CollisionTraverser()
        base.pusher = CollisionHandlerPusher()
    
    def initPlayer(self):
        """ loads the player and creates all the controls for him/her/them """
        self.node = Player(self)
        if base.isClient == False:
            # Make a psuedo client
            pseudoClient = ClientClass(None, 0, self.node)
            base.server.clients.append(pseudoClient)
    
    def addRemotePlayer(self, connection):
        """ adds a player on a remote connection"""
        
        remotePlayer = Player(self, Local = False, Client = connection, ID = len(base.server.players))
        base.server.players.append(remotePlayer)
        return remotePlayer
    
    def addServerPlayer(self, ID, isme):
        serverPlayer = Player(self, Local = isme, Client = None, ID = ID)
        if isme: base.controlPlayer = serverPlayer
        base.serverConnection.players.append(serverPlayer)
        return serverPlayer
    
    def initLighting(self):
        alightnode = AmbientLight("ambient light")
        alightnode.setColor(Vec4(0.4,0.4,0.4,1))
        alight = base.render.attachNewNode(alightnode)
        render.setLight(alight)
        
        dlight = DirectionalLight('dlight') 
        dlight.setColor(VBase4(0.5, 0.5, 0, 1)) 
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        base.lightable.setLight(dlnp)
        base.plnp = dlnp


FPS()
#mainMenu()
#PStatClient.connect()
run() 
