from pandac.PandaModules import *
from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from gameconnection import *

class ServerConnectionClass(GameConnection):
    ##########################
    # Client Side EVERYTHING #
    ##########################
    def InitClient(self, ip_address = "127.0.0.1"):
        """ Initializes a client connection on this gameconnection """
        self.InitServer = self.LockOut
        self.Server = False
        
        port_address = 9099
        #ip_address = "127.0.0.1"
        timeout_in_miliseconds = 3000
        
        print "Connecting client to", ip_address, ":", port_address
        
        self.myConnection = self.cManager.openTCPClientConnection(ip_address, port_address,
                                                             timeout_in_miliseconds)
        if self.myConnection:
            self.cReader.addConnection(self.myConnection)
            taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)
            
            print "Client connected to", ip_address
    
    def handleClientPacket(self, datagram):
        myIterator = PyDatagramIterator(datagram)
        msgID = myIterator.getUint8()
        
        if msgID == 16:
            # Add a player to the array
            controlling = myIterator.getBool()
            ID = myIterator.getUint8()
            player = self.game.addServerPlayer(ID, controlling)
            
            player.node.setX(myIterator.getFloat64())
            player.node.setY(myIterator.getFloat64())
            player.node.setZ(myIterator.getFloat64())
            
            player.node.setH(myIterator.getFloat64())
            player.node.setP(myIterator.getFloat64())
        elif msgID == 102:
            # Heartbeat
            pass
        elif msgID == 202:
            # Got a player position update message
            # Find indicated player
            ID = myIterator.getUint8()
            for Splayer in self.players:
                if Splayer.ID == ID:
                    player = Splayer
                    break
            
            # Apply data
            player.node.setX(myIterator.getFloat64())
            player.node.setY(myIterator.getFloat64())
            player.node.setZ(myIterator.getFloat64())
            
            # Only update for remote clients
            if ID != base.controlPlayer.ID:
                player.node.setH(myIterator.getFloat64())
                player.node.setP(myIterator.getFloat64())
            return
        
        print "Client got a message of type", msgID
        