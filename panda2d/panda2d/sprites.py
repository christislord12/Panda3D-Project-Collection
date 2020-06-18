# -*- coding: utf-8 -*-
""" This allows to manage Animated Sprites and spritesheets as made with darkFunction Editor.
darkfunction.com/editor/
"""

#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import NodePath
from pandac.PandaModules import CardMaker
from pandac.PandaModules import Vec4, Vec3, Vec2
from pandac.PandaModules import TextureStage

from panda3d.core import Texture, BitMask32, TextNode
from panda3d.core import CollisionNode, CollisionSphere

from xmlDao import Dao

class SimpleSprite(NodePath):
	def __init__(self, texture, parent=None, pos=Vec3(0,0,0) , rect=None, name="spritesMaker"):
		self.cm = CardMaker(name)
		#read note on animated sprite
		self.cm.setFrame(-0.5, 0.5, -0.5, 0.5)
		#self.cm.setHasUvs(True)
		NodePath.__init__(self, self.cm.generate())
		ts = TextureStage.getDefault()
		#tx, ty = texture.getXSize(), texture.getYSize()
		tx, ty = texture.getOrigFileXSize(), texture.getOrigFileYSize() #to compensate for upscaled texture
		if not rect:
			rect = Vec4(0, 0, tx, ty)

		self.rect = rect
		self.setTexture(texture, 1)
		self.setPos(pos)
		self.setScale(rect[2], 1.0, rect[3])

		self.setTexScale(ts, rect[2]/tx, rect[3]/ty)
		#read animated sprite on notes
		ofx = rect[0]/tx
		ofy = (rect[1]+rect[3])/ty
		self.setTexOffset(ts, ofx, -ofy)
		self.reparentTo(parent)
		self.setTransparency(True)

	def scaleBy(self, x, y=None):
		if y is None: y = x
		self.setScale(self.rect[2]*x, 1.0, self.rect[3]*y)

class SpriteDef():
	def __init__(self, name, coords):
		self.name = name
		self.rotate = False
		x,y,w,h = coords
		self.pos = Vec2(x, y)
		self.size = Vec2(w, h)
		self.rect = Vec4(self.pos[0], self.pos[1], self.size[0], self.size[1])
		self.orig = Vec2(w/2, h/2)
		#self.offset = Vec2(*map(float, lines.pop(0).split(":")[1].split(",")))
		#self.index = int(lines.pop(0).split(":")[1])

#TODO dfE goes crazy with subfolders, fix it
class Frame():
	def __init__(self, idn, delay, sprites):
		self.idx, self.delay, self.sprs = idn, delay, sprites
		s = self.sprs[0]
		self.name = s[0] #TODO have many sprites ?
		self.offset = Vec2(s[1], s[2])

class Animation():
	def __init__(self, name, loops, frames):
		self.name = name
		self.loops = loops
		self.looping = True
		self.frames = tuple((Frame(*f) for f in frames))
		#print('frames', self.frames)

class AnimatedSprite(NodePath):
	state = -1
	task = None
	_loops = 0
	cnodep = None
	def __init__(self, atlas, parent, name='AnimatedSprite'):
		self.atlas = atlas
		self.name = name
		self.cm = CardMaker('CM'+name)
		#|Craig| suggested this was the correct signs
		NodePath.__init__(self, 'P'+name)
		self.cm.setFrame(-0.5, 0.5, -0.5, 0.5)
		#CAREFUL
		#self.cm.setHasUvs(True)
		#if we set HasUvs then as the coords are -Z,
		# the last point have to be -0.5 or it will be mirrored (-0.5, 0.5, 0.5, -0.5)
		#i have no idea which is the best way but i assume 1 less uv is faster.
		#also requires less modification
		#Using 0.5 for the extremes makes the texture look better, dunno why, also is easier to transform and some animations would
		#require centering by nature, so is best to use that.

		cmn = self.cm.generate()
		self.card = self.attachNewNode(cmn)
		#NodePath.__init__(self, self.cm.generate())

		self.card.setTexture(atlas.texture, 1)
		self.tx, self.ty = atlas.texture.getXSize(), atlas.texture.getYSize()#Ojo con el power of 2
		self.ts = TextureStage.getDefault()
		self.reparentTo(parent)
		self.setTransparency(True)

	def debug(self, text, scale=13): # this is the best thing that i could have done
		if not hasattr(self, "_tn"):
			textn = TextNode("debug textnode")
			textn.setTextColor(1.0, 0.2, 0.2, 1.0)
			self._tn = self.attachNewNode(textn)
			self._tn.setPos(-20, -1, -20)
		self._tn.setScale(scale)
		self._tn.node().setText(str(text))

	def setCollide(self, owner=None, show=False):
		#owner sets the tag "owner" to get the python object in a collision
		cs = CollisionSphere(0, 0, 0, 0.8)
		#cs = CollisionBox((0,-5,0), 1, 10, 1)
		cn = CollisionNode('CN'+self.name)
		cn.setFromCollideMask(BitMask32(0x10))
		cn.setCollideMask(BitMask32(0x10))
		cnodePath = self.card.attachNewNode(cn)
		cnodePath.node().addSolid(cs)

		if show: cnodePath.show()
		cnodePath.setColorScale(0.1,0.1,0.1,0.1)

		if not owner: owner = self
		cnodePath.node().setPythonTag("owner", owner)
		self.cnodep = cnodePath
		
	def setFrame(self, frame):
		sp = self.atlas.sprites[frame.name]
		rect = self.rect = sp.rect
		self.card.setScale(rect[2], 1.0, rect[3])
		self.card.setTexScale(self.ts, rect[2]/self.tx, rect[3]/self.ty)

		ofx = rect[0]/self.tx
		#Vs are negative so i must add the sprite size
		ofy = (rect[1]+rect[3])/self.ty
		#vs are negative so i must substract it
		self.card.setTexOffset(self.ts, ofx, -ofy)
		#i really really would love to not have to do all this kind of stuff.
		#having one point of reference (top-left==0,0) makes all this more natural and intuitive (which is not)
		#right now the node origin is bottomleft, the texture origin is bottomleft but the coords are -Y
		#the screen origin is bottom-left but also +Y
		
	def setSprite(self, spriteName):
		"""Sets a static sprite by its name
		@spriteName string with the name of the sprite
		"""
		fr = self.atlas.frameForSp(spriteName)
		self.setFrame(fr)
		
	def play(self, i):
		"""Starts playing an animation
		@i is the index of the animation
		current animation is stored in @self.state
		animation index can be obtained with atlas.animIndex("anim_name")
		"""
		self.anim = self.atlas.anims[i]
		self.state = i
		self.current = 0
		self._loops = 0
		if self.task :
			taskMgr.remove(self.task)
		self.task = taskMgr.doMethodLater(0, self.animate, 'animation')

	def stop(self):
		"""Stops an animation"""
		if self.task:
			taskMgr.remove(self.task)
			self.task = None

	def remove(self):
		"""Removes an animated sprite from the tree (it will get freed if there are no more references)"""
		self.stop()
		if self.cnodep:
			self.cnodep.node().setPythonTag("owner", None)
		self.removeNode()
		#self.delete()
		#self.ignoreAll()

	def animate(self, task):
		if not self.task : return task.done
		frame = self.anim.frames[self.current]
		task.delayTime = frame.delay
		self.setFrame(frame)

		self.current += 1
		if self.current >= len(self.anim.frames):
			self.current = 0
			#print ("anim", self.anim.loops, self._loops)
			self._loops += 1
			if (self.anim.loops>0) and (self._loops >= self.anim.loops):
				return task.done
		return task.again
	
	def addChild(self, np, off):
		#fake addChild because it doesnt quite work the hierarchy yet
		n = self.getParent()
		#print n
		np.reparentTo(n)
		from panda3d.core import CompassEffect
		np.setEffect(CompassEffect.make(self, CompassEffect.PPos))
		np.setPos(off)
		
class Atlas():
	texture = None
	anims = tuple()
	sprites = {}

	def __init__(self, dir="", fanim=None, fsprites=None ):
		if fanim or fsprites:
			self.loadXml(dir, fanim, fsprites)

	def animIndex(self, name):
		for i, a in enumerate(self.anims):
			if a.name == name:
				return i
		return -1
	
	def newSprite(self, spriteName, parent, name ="NewSprite"):
		an = AnimatedSprite(self, parent, name)
		#self.anims.append(Animation([spriteName, "{", "looping: false", "frame: %s,0,0,0"%spriteName, "}"]))
		#an.play(len(self.anims)-1)
		an.setFrame(self.frameForSp(spriteName))
		return an
	
	def frameForSp(self, spriteName):
		data = (0, 0, ( (spriteName, 0,0), ) )
		return Frame(*data)
	
	def loadXml(self, dir, fanim="", fsprites=""):
		fspa = ""
		if fanim: fspa = self._parseXmlAnims(dir+'/'+fanim)
		fsp = (fsprites or fspa)
		self._parseSpritesXml(dir, fsp)
	
	def _parseSpritesXml(self, dir, filename):
		print("spritesheet", filename)
		f = Dao('img', dir+'/'+filename)
		r = f.root()
		ftext = dir+'/'+r.name
		import panda2d
		self.texture = loader.loadTexture(ftext)
		self.texture.setMagfilter(panda2d.TXFILTER)
		self.texture.setMinfilter(panda2d.TXFILTER)
		if panda2d.ANI >1: self.texture.setAnisotropicDegree(panda2d.ANI)

		self.sprites = {}
		w = int(r.w)
		h = int(r.h)
		defs = r.definitions[0]
		#fake recursion cuz im lazy
		dirs = []
		dirs.extend(
			( (dd, '') for dd in defs.dir )
		)
		while dirs:#for each pseudo directory
			dd, parent = dirs.pop(0)
			name = dd.name
			#print (dd, parent, name)
			#path = parent+name+'/'
			#path = parent+'/'+name
			path = parent + name # TODO this sucks but thats how dfEditor works
			#path = parent
			#if parent: path += '/'
			#path += name
			if hasattr(dd, 'dir'):#if it has more pseudo directories (categories) in it, it add them to the "queue"
				#print (dd)
				dirs.extend(
					( (ddd, path) for ddd in dd.dir )
				)
			#add the sprites to this
			#path += '/'
			for spr in dd.spr:
				coords = tuple(map(int, (spr.x, spr.y, spr.w, spr.h)))
				name = path+spr.name
				sd = SpriteDef(name, coords)
				self.sprites[name] = sd
		#done

	def _parseXmlAnims(self, filename):
		self.anims = []
		spsheet = ''
		d = Dao('animations', filename)
		r = d.root()
		spsheet = r.spriteSheet
		ver = r.ver
		print ("animations file version", ver)
		for a in r.anim:
			name = a.name
			loops = int(a.loops)
			cells = []
			for c in a.cell:
				cc = [int(c.index), int(c.delay)/23.0]
				#dunno why 23, but it is the closes value that resembles the effect on the program
				#a delay of 10 synchronizes to Live Good (The Bloody Beetroots Remix) by Naive New Beaters
				ss = [ (s.name, int(s.x), int(s.y), int(s.z)) for s in c.spr ]
				cc.append(tuple(ss))
				cells.append(tuple(cc))
			#print cells
			self.anims.append(Animation(name, loops, cells))
		self.anims = tuple(self.anims)
		return spsheet
	#done

	def parse(self, dir, filename):
		f = open(dir+'/'+filename, "r")
		text = f.readline().strip()
		self.texture = loader.loadTexture(dir+'/'+text)
		self.texture.setMagfilter(panda2d.TXFILTER)
		self.texture.setMinfilter(panda2d.TXFILTER)
		self.sprites = {}
		format = f.readline().strip()
		filter = f.readline().strip()
		repeat = f.readline().strip()
		lines = []
		for line in f:
			lines.append(line.strip())
			if len(lines)== 7:
				sd = SpriteDef(lines)
				self.sprites[sd.name] = sd
				lines = [] #not necessary

	def parseAnims(self, filename):
		self.anims = []
		try:
			f = open(filename, 'r')
			lines = []
			for line in f:
				line = line.strip()
				lines.append(line)
				if line == "}":
					anim = Animation(lines)
					self.anims.append(anim)
					lines = []#necessary
		except:
			print ("No animations for this spritesheet (%s)" % filename)
		pass

