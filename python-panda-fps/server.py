from pandac.PandaModules import *
from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from gameconnection import *
from client import *

class ServerClass(GameConnection):
    activeConnections = []
    connectedClients = 0
    clients = []
    
    def __init__(self, game):
        GameConnection.__init__(self, game)
        self.InitServer()
    
    ##########################
    # Server Side EVERYTHING #
    ##########################
    def InitServer(self):
        """ Initializes a server on this gameconnection """
        
        port_address = 9099
        backlog = 1000
        self.tcpSocket = self.cManager.openTCPServerRendezvous(port_address, backlog)

        self.cListener.addConnection(self.tcpSocket)

        taskMgr.add(self.tskListenerPolling, "Poll the connection listener", -39)
        taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)
        taskMgr.add(self.tskXmitAll, "Transmit tick data")
        
        print "Server started on port", port_address
    
    # Tasks to maintain the listeners
    def tskListenerPolling(self, taskdata):
        if self.cListener.newConnectionAvailable():
     
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
     
            if self.cListener.getNewConnection(rendezvous,netAddress,newConnection):
                newConnection = newConnection.p()
                self.activeConnections.append(newConnection) # Remember connection
                self.cReader.addConnection(newConnection)    # Begin reading connection
                
                player = self.game.addRemotePlayer(self)              # Add a new player object
                newClient = ClientClass(newConnection, connectedClients, player)
                self.handleClientJoin(newClient)         # Send initial data to client
                self.onClientJoin(newClient)             # Callback
                
                connectedClients += 1
                
                print "Client connected from", netAddress
        return taskdata.cont
        
    def handleClientJoin(self, client):
        print "Handling client join", client
        
        playerID = client.ID
        
        for player in self.players:
            # Send our list of players to the client
            self.sendPlayerToClient(client, player, self.players.index(player), self.players.index(player) == playerID)
            # Sync time with client
            client.doHandshake()
        
    def sendPlayerToClient(self, clientTo, player, playerID, controlling):
        print "sending player", playerID, "to", clientTo
        # We are telling the client to make a player here
        datagram = PyDatagram()
        datagram.addUint8(16)
        # Client should control player?
        datagram.addBool(controlling)
        # ID of client/player we are adding
        datagram.addUint8(playerID)
        # attach position as 3 floats
        datagram.addFloat64(player.node.getX())
        datagram.addFloat64(player.node.getY())
        datagram.addFloat64(player.node.getZ())
        
        datagram.addFloat64(player.node.getH())
        datagram.addFloat64(player.node.getP())
        
        # Send message
        self.cWriter.send(datagram, clientTo)
    
    def sendHandshakeToClient(self, clientTo):
        datagram = PyDatagram()
        # Handshake packet
        datagram.addUint8(1)
        # Server time
        datagram.addFloat64(time.time())
        clientTo
        # 
    
    def handleServerPacket(self, datagram):
        myIterator = PyDatagramIterator(datagram)
        msgID = myIterator.getUint8()
        
        source = datagram.getConnection()
        ID = self.remoteConnections.index(source) + 1
        
        if msgID == 200:
            # Player sent a movement packet
            self.players[ID].walk = Vec3(0, myIterator.getFloat64(), 0)
            self.players[ID].strafe = Vec3(myIterator.getFloat64(), 0, 0)
            self.players[ID].readyToJump = myIterator.getBool()
            self.players[ID].jet = myIterator.getBool()
            if ID == 1:
                # Temp screen text
                if self.position is None: self.position = OnscreenText(text = "0", pos = (-0.3,-0.3), 
                    scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
                else: self.position.setText(str([self.players[1].walk, self.players[1].strafe, self.players[1].readyToJump, self.players[1].jet]))
            return
        elif msgID == 201:
            # Player sent a rotation packet
            self.players[ID].node.setH(myIterator.getFloat64())
            self.players[ID].node.setP(myIterator.getFloat64())
            # This would apply to camera, but I'll leave it in if we need it later for animations of the head, or something
            #self.players[1].node.setR(myIterator.getFloat64())
            if ID == 1:
                # Temp screen text
                if self.position is None: self.position = OnscreenText(text = "0", pos = (-0.3,-0.3), 
                    scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
                else: self.position.setText(str([self.players[1].walk, self.players[1].strafe, self.players[1].readyToJump, self.players[1].jet]))
            return
            
        print "Server got a message of type", msgID
    
    def tskXmitAll(self, taskdata):
        """ Transmit all data about positions, rotations, etc. """
        #print "building", str(len(self.remoteConnections)*len(self.players)), "packets"
        #for connection in self.remoteConnections:
        for client in self.clients:
            player = client.player
            # Build packet
            datagram = PyDatagram()
            datagram.addUint8(202)
            # ID of player object
            datagram.addUint8(player.ID)
            # ZYX/HPR
            datagram.addFloat64(player.node.getX())
            datagram.addFloat64(player.node.getY())
            datagram.addFloat64(player.node.getZ())
            
            datagram.addFloat64(player.node.getH())
            datagram.addFloat64(player.node.getP())
            #datagram.addFloat64(player.node.getR())
            for connection in self.activeConnections:
                self.cWriter.send(datagram, connection)
                
        return taskdata.cont