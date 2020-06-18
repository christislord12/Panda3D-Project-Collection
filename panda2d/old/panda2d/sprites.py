# -*- coding: utf-8 -*-
#from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import NodePath
from pandac.PandaModules import CardMaker
from pandac.PandaModules import Vec4, Vec3, Vec2
from pandac.PandaModules import TextureStage
from panda3d.core import Texture

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
	def __init__(self, lines):
		self.name = lines.pop(0)
		self.rotate = lines.pop(0) == True
		self.pos = Vec2(*map(float, lines.pop(0).split(":")[1].split(",")))
		self.size = Vec2(*map(float, lines.pop(0).split(":")[1].split(",")))
		self.rect = Vec4(self.pos[0], self.pos[1], self.size[0], self.size[1])
		self.orig = Vec2(*map(float, lines.pop(0).split(":")[1].split(",")))
		self.offset = Vec2(*map(float, lines.pop(0).split(":")[1].split(",")))
		self.index = int(lines.pop(0).split(":")[1])

class Animation():
	def __init__(self, lines):
		self.name = lines.pop(0)
		lines.pop(0) #{
		self.looping = lines.pop(0).split(":")[1].strip().lower() == "true"
		self.frames = [Frame(line) for line in lines if line.startswith("frame:")]

class Frame():
	def __init__(self, line):
		its = line.split(":")[1].split(",")
		self.name = its.pop(0).strip()
		self.delay = int(its.pop())/1000.0
		self.offset = Vec2(*map(float, its))

class Atlas():
	def __init__(self, dir, name):
		self.parse(dir, name+".sprites")
		self.parseAnims(dir+'/'+name+".animations")

	def parse(self, dir, filename):
		f = open(dir+'/'+filename, "r")
		text = f.readline().strip()
		self.texture = loader.loadTexture(dir+'/'+text)
		self.texture.setMagfilter(Texture.FTLinearMipmapLinear)
		self.texture.setMinfilter(Texture.FTLinearMipmapLinear)
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

	def createSprite(self, spriteName, parent):
		an = AnimatedSprite(self, parent)
		#self.anims.append(Animation([spriteName, "{", "looping: false", "frame: %s,0,0,0"%spriteName, "}"]))
		#an.play(len(self.anims)-1)
		an.setFrame(Frame("frame: %s,0,0,0"%spriteName))
		return an

	def animIndex(self, name):
		for i, a in enumerate(self.anims):
			if a.name == name:
				return i
		return -1

class AnimatedSprite(NodePath):
	state = -1
	task = None
	def __init__(self, atlas, parent):
		self.atlas = atlas
		self.cm = CardMaker('spritesMaker')
		#|Craig| suggested this was the correct signs

		self.cm.setFrame(-0.5, 0.5, -0.5, 0.5)
		#CAREFUL
		#self.cm.setHasUvs(True)
		#if we set HasUvs then as the coords are -Z,
		# the last point have to be -0.5 or it will be mirrored (-0.5, 0.5, 0.5, -0.5)
		#i have no idea which is the best way but i assume 1 less uv is faster.
		#also requires less modification
		#Using 0.5 for the extremes makes the texture look better, dunno why, also is easier to transform and some animations would
		#require centering by nature, so is best to use that.


		NodePath.__init__(self, self.cm.generate())

		self.setTexture(atlas.texture, 1)
		self.tx, self.ty = atlas.texture.getXSize(), atlas.texture.getYSize()
		self.ts = TextureStage.getDefault()
		self.reparentTo(parent)
		self.setTransparency(True)

	def setFrame(self, frame):
		sp = self.atlas.sprites[frame.name]
		rect = sp.rect
		self.setScale(rect[2], 1.0, rect[3])
		self.setTexScale(self.ts, rect[2]/self.tx, rect[3]/self.ty)

		ofx = rect[0]/self.tx
		#Vs are negative so i must add the sprite size
		ofy = (rect[1]+rect[3])/self.ty
		#vs are negative so i must substract it
		self.setTexOffset(self.ts, ofx, -ofy)
		#i really really would love to not have to do all this kind of stuff.
		#having one point of reference (top-left==0,0) makes all this more natural and intuitive (which is not)
		#right now the node origin is bottomleft, the texture origin is bottomleft but the coords are -Y
		#the screen origin is bottom-left but also +Y

	def play(self, i):
		self.anim = self.atlas.anims[i]
		self.state = i
		self.current = 0
		if self.task :
			taskMgr.remove(self.task)
		self.task = taskMgr.doMethodLater(0, self.animate, 'animation')

	def stop(self):
		if self.task:
			taskMgr.remove(self.task)
			self.task = None

	def animate(self, task):
		frame = self.anim.frames[self.current]
		task.delayTime = frame.delay
		self.setFrame(frame)

		self.current += 1
		if self.current >= len(self.anim.frames):
			self.current = 0
			if not self.anim.looping:
				return task.done
		return task.again




