# Networking modules
from pandac.PandaModules import *
from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

# Prototyping modules REMOVE
from direct.gui.OnscreenText import OnscreenText

class GameConnection():
    def __init__(self, game):
        # Init some objects
        print "Game connection initialized"
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.game = game
    
    
    ##########################
    # Either Side EVERYTYING #
    ##########################

    def tskReaderPolling(self, taskdata):
        while self.cReader.dataAvailable():
            datagram = NetDatagram()  # catch the incoming data in this instance
            # Check the return value; if we were threaded, someone else could have
            # snagged this data before we did
            if self.cReader.getData(datagram):
                if self.Server: self.handleServerPacket(datagram)
                else: self.handleClientPacket(datagram)
        return taskdata.cont

    def terminate(self):
        print "Terminating", self
        if self.Server:
            for aClient in activeConnections:
                self.cReader.removeConnection(aClient)
            self.activeConnections = []
            self.cManager.closeConnection(self.tcpSocket)
        else:
            self.cReader.closeConnection(self.myConnection)
    
    def doPacket(self, ID, structure, data):
        datagram = PyDatagram()
        datagram.addUint8(ID)
        for number in range(len(structure)):
            letter = structure[number]
            dat = data[number]
            if letter == "b": datagram.addInt8(dat)
            elif letter == "B": datagram.addInt8(dat)
            elif letter == "F": datagram.addFloat64(dat)
            elif letter == "!": datagram.addBool(dat)
        
        self.cWriter.send(datagram, self.myConnection)

    # Handlers n stuff
    
    def attachPlayer(self, player):
        self.player = player
    
    # Callbacks
    def onClientJoin(self, connection):
        pass