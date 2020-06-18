// server.js
// test server for "net ralph" on node.js
// (c) gsk 08/2012

var net = require('net');

var SERVER_VERSION = '0.0.3';
var STARTUP_TIME = new Date().getTime();

// define opcodes and message sizes
var rpc_ops = {
    1  : 21,    // create player
    2  : 21,    // create actor
	3  : 21,	// object state update
    4  : 4,     // delete object
    5  : 8      // ping message with timestamp
};

// create an object state/position update type message packet
// currently three different messages use this
// opcode 1 : create player avatar actor
// opcode 2 : create generic actor
// opcode 3 : object state/position update
var stateMessage = function(opcode, objid, state, xpos, ypos, zpos, hdg) {
	
	// message size (bytes): 
    // opcode (2) + objid (2) + state (1) + xpos (4) + ypos (4) + zpos (4)  + hdg (4) = 21
	// pack everything into a buffer
	
	buf = new Buffer(21);
	buf.writeUInt16LE(opcode, 0);	    // opcode
	buf.writeUInt16LE(objid, 2);	    // object id
	buf.writeUInt8(state, 4);  	        // state
	buf.writeFloatLE(xpos, 5);		    // xpos
	buf.writeFloatLE(ypos,9); 		    // ypos
	buf.writeFloatLE(zpos,13);		    // zpos
	buf.writeFloatLE(hdg,17);		    // heading
		 
	return buf;
};

var deleteObjectMessage = function(objid) {
	// message size (bytes): opcode (2) + objid (2) = 4
	buf = new Buffer(4);
	buf.writeUInt16LE(4, 0);	        // opcode 4
	buf.writeUInt16LE(objid, 2);	    // object id
    return buf;
};

var pingMessage = function(timestamp, lag) {
	// message size (bytes): opcode (2) + timestamp (4) + lag (2)  = 8
	buf = new Buffer(8);
	buf.writeUInt16LE(5, 0);	        // opcode 5
	buf.writeUInt32LE(timestamp, 2);	// timestamp
	buf.writeUInt16LE(lag, 6);	        // current lag
    return buf;
};

// ----------------------------------------------------------------------------
// a client object gets created by the connection listener for all connections

var Client = {
    
    // these are the attributes describing the player's avatar object
	id : 0,             // this is the client ID which is the same as the objects avatar ID 
    state : 0x0,        // initial state should be IDLE
	xpos : -107.5,
	ypos : 26.6,
	zpos : -0.49,
    hdg : 0.0,
    
    // this stuff is for network message processing on this client connection
	netbufsize : 8192,
	inbuf : new Buffer(8192),
	opbuf : new Buffer(512),	// maximum size for a single operation packet = 512
	readp : 0,
	writep: 0,
		
    // misc. variables related to the management of this client connection
    timer_id : 0,
    current_lag : 0,
    
	// this actually implements three different operations that all need to transmit basically 
	// the same information with differing opcodes:
	// 1: create player
	// 2: create actor
	// 3: send state update
	sendState : function(s, op) {
		// console.log('id:', this.id, ' sending op:',op, ' to socket id:', s.id);
		
		// buffer based binary message
		msg = stateMessage(op, this.id, this.state, this.xpos, this.ypos, this.zpos, this.hdg);
		// console.log('binary buffer msg: ', msg);
	  	s.write(msg, function (){ 
	  		// console.log('connection id:',s.id,'flushed');
	  	});		
	},

    // Send a message on all sockets other than the sending client's
    // parameters
    // clist :  the list of clients (sockets) 
    // message : well, the message we want to send.
	broadcastMessage : function(clist, message) {
		for (key in clist) {
			if (clist[key].id != this.id)               
                clist[key].socket.write(message);
		}
	},
	
	// Send position updates to all clients other than the owner of this client object
	broadcastState : function(clist) {
		// console.log('sending my (id:', this.id,') state to ', Object.keys(clist).length-1, ' entities.'); 
        msg = stateMessage(3, this.id, this.state, this.xpos, this.ypos, this.zpos, this.hdg);
        this.broadcastMessage(clist, msg);
	},

	// This actually spawns the player avatar objects on clients
	// send our initial state to all objects in scope
	// this includes ourselves
	broadcastInitialState : function(clist) {
		console.log('spawning object (id:', this.id,') on ', Object.keys(clist).length, ' entities.'); 
		for (key in clist) {
			if (clist[key].id == this.id)
				op = 1;		// send 'createPlayer' to the controlling client
			else
				op = 2;		// send 'createActor' to all others
				
			this.sendState(clist[key].socket, op);
		}
	},
   
	// start up a new client: 
	// make the new player avatar spawn on all clients (including the new one)
	// and make all prior existing client avatars spawn on the new client
	startupClient : function(clist) {
		
        // start our avatar on all clients including our own
		this.broadcastInitialState(clist);
		
		// now start all prior existing avatars on our own client
		for(key in clist) {
			c = clist[key];
			if (c.id != this.id) {
				// console.log('making client id:', c.id, 'send createActor to id:', this.id);
				c.sendState(this.socket, 2);
			}
		}		

        // install the regular keepalive ping: right now we send every 2 seconds
        // This is also used to measure current roundtrip time for this client
        // NOTE: that the callback function will be excuted in a separate context!
        // For this reason, "this" will not point to this client object!
        this.timer_id = setInterval( function(client) {
            timestamp = new Date().getTime() - STARTUP_TIME;
            lag = client.current_lag;
            if (lag > 65535)
                lag = 65535;    // clamp lag to 16 bits
            // console.log('ping:', timestamp, ' lag:', lag);
            msg = pingMessage(timestamp, lag);
            client.socket.write(msg);
        }, 2000, this);
        
	},
	
    cleanup : function() {
        console.log('performing cleanup for connection ', this.id);
        
        // remove our regular keepalive timer
        clearInterval(this.timer_id);
        // inform everyone else of our exit
        this.broadcastMessage(server.clist, deleteObjectMessage(this.id));
        // delete ourselves from the servers list of connections
       	delete server.clist[this.id.toString()];
    },
    
	// ------------------------------------------------------------------------
	// incoming network data processing
	
    // client sent a position/state update for its player avatar object:
    // broadcast to the rest of the world
	processRpcOp : function(opcode, opdata) {
		switch(opcode) {
			
            case 3:
                // client state update
				objid = opdata.readUInt16LE(2);
				this.state= opdata.readUInt8(4);
				// console.log('processing rpc op: client object position update for object id=', objid, ' state=', this.state);
            
                // note that in production code we wont be able to simply accept an
                // unchecked position from a client anymore !
                this.xpos = opdata.readFloatLE(5);
                this.ypos = opdata.readFloatLE(9);
                this.zpos = opdata.readFloatLE(13);
                this.hdg = opdata.readFloatLE(17);
                this.broadcastState(server.clist);
				break;
            
            case 5:
                // keepalive ping from client: this contains our original 
                // timestamp which we now use to measure current network
                // roundtrip time (aka "lag")
                sent_time = opdata.readUInt32LE(2);
                current_time = new Date().getTime() - STARTUP_TIME;
                roundtrip_time = current_time - sent_time;
                this.current_lag = roundtrip_time;
                // console.log('received a return ping, roundtrip time:', roundtrip_time, 'ms');
                break;
		}
	},
	
	// stuff all incoming data into the client's network data inbuf
    // check if any complete messages have arrived and if so, determine and execute the respective rpc function
	processClientData : function(data) {
		// console.log('client data received, len: ', data.length, ' ', data.toString());
		data.copy(this.inbuf, this.writep, 0, data.length);
		this.writep+=data.length;
		bytes_left = this.writep - this.readp;
		while (bytes_left >= 2) {
			opcode = this.inbuf.readUInt16LE(this.readp);
			// console.log('writep:', this.writep, ' readp:',this.readp, ' incoming opcode:', opcode);
            if (typeof rpc_ops[opcode] == "undefined"){
                // got an undefined opcode on this connection, could be a network error
                // more likely its someone messing around though! Kick them out!
                console.log('ERROR: received undefined opcode ', opcode, ' on connection ', this.id);
                this.socket.destroy();
                return;
            }
			oplen = rpc_ops[opcode]
			if (bytes_left >= oplen) {
				// console.log('complete op in buffer, oplen:', oplen);
				this.inbuf.copy(this.opbuf, 0, this.readp, this.readp+oplen);
				this.readp = this.readp + oplen;
				bytes_left = this.writep - this.readp;				
				this.processRpcOp(opcode, this.opbuf);
			} else {
				console.log('Fragmented OP in network inbuf! No fragment handling implemented. \nData will be lost!');
			}
		}
		// buffer data has been completely digested: reset buffer write/read pointers
		this.writep = this.readp = 0;
	}
};


// ----------------------------------------------------------------------------
// client connection listener
var onConnect = function(socket) {

	socket.setNoDelay(true);
	
	// start up a new client upon connection
  	console.log('client connected, id:', server.connection_id, ' remote ip:', socket.remoteAddress);
  	console.log('starting up remote player ')
  	
  	id = server.connection_id++;  	
  	socket.id = id;  	
  	c = Object.create(Client);      // create the client object
  	c.id = socket.id;				// store the id (same as socket.connection_id)
	c.socket = socket;				// store the socket
	
  	c.xpos = -107.5;				// store the standard starting position
  	c.ypos = 26.6;
  	c.zpos = -0.49;
  	
  	socket.client = c;					    // store the client object with the socket too
  	server.clist[c.id.toString()] = c;	    // store the client object in the server's list
	
	c.startupClient(server.clist);	// startup the new client

	// set callback for disconnect (initiated by the client)
  	socket.on('end', function() {
    	console.log('client disconnected, id:', this.id);
        // let the client object cleanup itself before we destroy it
    	client = server.clist[this.id.toString()];
        if (typeof(client) != 'undefined')
            client.cleanup();
  	});

	// set callback for network errors
  	socket.on('error', function() {
    	console.log('network error on connection id:', this.id, '. Disconnecting');
        // let the client object cleanup itself before we destroy it
    	client = server.clist[this.id.toString()];
        if (typeof(client) != 'undefined')
            client.cleanup();
  	});

	// set callback for socket close events
    // Note that this will be emitted in addition to the 'end' event 
    // for client disconnects
  	socket.on('close', function() {
    	console.log('socket closed on connection id:', this.id);
        // let the client object cleanup itself before we destroy it
    	client = server.clist[this.id.toString()];
        if (typeof(client) != 'undefined')
            client.cleanup();
    });
  
	// set callback for incoming data
  	socket.on('data', function(data) {
  		this.client.processClientData(data);
  	});

};


// ----------------------------------------------------------------------------
// create our server

var server = net.createServer();
server.name = 'Node Game Server';
server.connection_id = 0;
server.clist = {};
server.on('connection', onConnect);

server.listen(8124, function() { //'listening' listener
  	console.log('server v', SERVER_VERSION, ' bound to port 8124 and listening ...');
});
