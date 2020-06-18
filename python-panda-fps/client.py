from pandac.PandaModules import *
from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from gameconnection import *

class ClientClass:
    def __init__(self, connection, ID, player):
        self.connection = connection
        self.ID = ID
        self.player = player
    
    