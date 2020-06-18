import sys
import struct
from asyncore import dispatcher
import socket

from panda3d.core import Vec3

# this inherits from asyncore.dispatcher for our networking needs
class GameClient(dispatcher):

    def __init__(self, world):
        dispatcher.__init__(self)
        self.world = world
        world.client = self
        
        self.id = None
        self.msg_buffer = ""    # buffer for incoming raw data

        # The dictionary of rpc operations
        # The opcode is the key to a tuple containing the function to be executed
        # and the byte length of the raw message for the rpc operation
        self.rpc_ops = { 
                            1 : [self.op_createPlayer, 21],
                            2 : [self.op_createActor, 21],
                            3 : [self.op_updateObjectPosition, 21],
                            4 : [self.op_deleteObject, 4],
                            5 : [self.op_ping, 8]
                            }

    # -------------------------------------------------------------------------
    # asyncore network code overrides
    def connect(self, host, port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)      # create a TCP socket
        dispatcher.connect(self, (host, port))                      # and connect
    
    def handle_connect(self):
        print 'connected'

    def handle_close(self):
        print 'disconnecting'
        sys.exit(1)

    # Implement me: add buffer handling code here to make our sending more reliable (buffering)!
    def handle_write(self):
        pass
        
    def handle_read(self):
        ''' we can pump the incoming data directly into processNetworkData because
            that function does its own buffering '''
        self.processNetworkData(self.recv(8192))    # receive max. 8192 bytes at once


    # -------------------------------------------------------------------------
    # Process incoming raw network data
    # all messages packets start with a 16bit opcode which tells us the message
    # type and, implicitly, the message length
    def processNetworkData(self, data):
        self.msg_buffer = self.msg_buffer + data        # buffer the incoming data
        bytes_left = bytes_in_buffer = len(self.msg_buffer)
        
        # process our buffer: try and extract all complete messages that have been buffered so far
        rindex = 0
        while (bytes_left >=2):             # at least one opcode in buffer
            (opcode,) = struct.unpack("<H", self.msg_buffer[rindex:rindex+2])
            # print 'network mesage received, opcode:', opcode
            oplen = self.rpc_ops[opcode][1]
            if( bytes_left >= oplen):       # enough data in buffer
                # print 'complete op (oplen:', oplen, ') in buffer, processing...'
                opbuf = self.msg_buffer[rindex:rindex+oplen]
                func = self.rpc_ops[opcode][0]
                func(opbuf)                         # execute

                rindex = rindex+oplen               # housekeeping: advance index
                bytes_left = bytes_left - oplen     # account for bytes processed
            else:
                print 'Incomplete op fragment in network buffer!'
                return

        # all data has been digested, reset buffer
        self.msg_buffer = ''
        
    # we send one of these to the server whenever our state changes due to user input
    # the server will then relay these messages to all other clients
    def sendClientPositionUpdate(self, objid, state, pos, hdg):
        # opcode 3: object position update
        # this contains: opcode, objid, state and 4 floats with the object's position and heading
        # movememnt state has bits for 'moving fwd', 'moving backwards', 'rotating right' , 'rotating left'
        msg = struct.pack("<HHBffff", 3, objid, state, pos[0], pos[1], pos[2], hdg)
        self.send(msg)

    # -------------------------------------------------------------------------
    # handlers for messages coming from the server
    def op_createPlayer(self, opbuf):
        print "op: create player, len(opbuf):", len(opbuf)
        (opcode, objid, state, xpos, ypos, zpos, hdg) = struct.unpack("<HHBffff", opbuf)
        print 'opcode:', opcode, ' objid:',objid,' state:',state,' xpos:', xpos, ' ypos:', ypos, 'zpos:', zpos
        self.id = objid     #store the player actor object id also as client id
        player = self.world.createActor(self.id, Vec3(xpos, ypos, zpos), self)
        self.world.createPlayer(player)

    def op_createActor(self, opbuf):
        print "op: create actor, len(opbuf):", len(opbuf)
        (opcode, objid, state, xpos, ypos, zpos, hdg) = struct.unpack("<HHBffff", opbuf)
        print 'opcode:', opcode, ' objid:', objid, 'state:', state,' xpos:', xpos, ' ypos:', ypos, 'zpos:', zpos
        player = self.world.createActor(objid, Vec3(xpos, ypos, zpos), self)

    def op_updateObjectPosition(self, opbuf):
        (opcode, objid, state, xpos, ypos, zpos, hdg) = struct.unpack("<HHBffff", opbuf)
        # print "op: update object position, object id=", str(objid)
        pos = Vec3(xpos, ypos, zpos)
        object = self.world.getObject(objid)
        if object is not None:
            object.motion_controller.saveNetState([state, pos, hdg])
        
    def op_deleteObject(self, opbuf):
        (opcode, objid) = struct.unpack("<HH", opbuf)
        print 'processing deleteObject message, objid=', objid
        self.world.deleteObject(objid)

    def op_ping(self, opbuf):
        (opcode, timestamp, lag) = struct.unpack("<HIH", opbuf)
        print 'processing ping message, incoming timestamp:', timestamp, ' server lag:', lag
        self.world.inst8.setText('Current connection lag: ' + str(lag) + ' ms')
        # simply send it back
        msg = struct.pack("<HIH", 5, timestamp, lag)
        self.send(msg)
        

        
