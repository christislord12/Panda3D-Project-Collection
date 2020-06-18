
# -*- coding: utf-8 -*-
import random as rd
rd.seed()

import panda2d.sprites
#from direct.showbase import DirectObject #input
from pandac.PandaModules import NodePath
from direct.interval.LerpInterval import LerpColorInterval, LerpHprScaleInterval, LerpPosHprScaleInterval, LerpPosInterval
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from pandac.PandaModules import Vec4, Vec3, Vec2

import whales.config


class Ship(panda2d.sprites.AnimatedSprite):
	hate = 0
	MAX_HATE = 2500
	def __init__(self, atlas, node, w):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, 'ship')
		self.w = w
		self.play(self.atlas.animIndex("Ship"))
		self.setPos(self.w.tilemap.pw/2.0, 0, -500)#self.w.tilemap.ph-200)
		self.setScale(3)
		self.setY(self.w.floor_y-2.5)

	def go(self):
		LerpPosInterval(self, 8, self.getPos()+Vec3(0, 0, 2000), self.getPos()).start()

	def hear(self, f, v):
		v = v/whales.config.VOLUME
		self.hate += v
		if (self.hate > self.MAX_HATE):
			self.w.lose()
		if self.hate <0: self.hate = 0

	def bomb(self):
		pass #no time for this, create a class for bomb, create an animation of a bomb, set the animation,
	#create a task for spawning them randomly, create a stop for that task

class Mic(panda2d.sprites.AnimatedSprite):
	bs = 0.5
	def __init__(self, atlas, node, w):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, 'screen')
		self.setSprite("/ic/mic")
		self.w = w
		t,b, w, h = self.rect
		self.setPos(
			self.w.tilemap.pw-w/4, self.getY(), 0+h/4.0
		)
		self.setScale(self.bs)

	def show(self, tf):
		scale = max(self.bs*tf[1]/whales.config.VOLUME/1.5, self.bs/4.0)
		self.setScale(scale)
		v = tf[0]/whales.config.MAX_FREQ
		ec = (v,v,v,1)#(r, g, b, 1.0)
		#print(scale,ec)
		#dt = globalClock.getDt()
		self.setColorScale(ec)
		#self.colorScaleInterval(dt, ec, self.getColorScale()).start()

class Screen(panda2d.sprites.AnimatedSprite):
	def __init__(self, atlas, node, real=True):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, 'screen' )
		self.setSprite("/screen")
		self.setX(300)
		self.setZ(240)

class Heart(panda2d.sprites.AnimatedSprite):
	OFF = "/ic/heart_off"
	ON = "/ic/heart_on"
	def __init__(self, atlas, node, on=True):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node )
		self.turn(on)

	def turn(self, on=True):
		icon = on and self.ON or self.OFF
		self.setSprite(icon)


WHALES = ('0', '1', '2', '3', '4', '5' )
S_WHALE = ('0.mp3', '1.mp3', '2.mp3', '3.mp3', '4.mp3', '5.mp3' )
#TODO this should be the sound files
class Whale(panda2d.sprites.AnimatedSprite):
	SWIMMING = 0
	DEAD = 100
	state = 0
	MAX_LOVE = 3
	sp = 15
	love = 0
	heart = None
	heart_bs = 2

	def __init__(self, atlas, node, world, wi = -11):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, 'whale' )
		if wi < 0 :
			wi = int(rd.random()*len(WHALES))
		who = WHALES[wi % len(WHALES)]
		self.w = world
		self.i = wi
		self.setSprite('/'+who)
		self.setX(300)
		self.setZ(240)
		self.setScale(0.2)
		self._tstroll = None
		self._tmove = None
		self._tbeat = taskMgr.doMethodLater(1, self.beat, 'bbeat')
		self.startStroll()
		self.setColor(0,0,0,0)
		LerpColorInterval(self, 2, (1, 1, 1, 1)).start()

	def hear(self, i, v):
		on = i == self.i
		if on :
			self.showLove(v)
		else:
			self.showLove(-0.1)

	def showLove(self, v):
		self.love = self.love +(v/100.0)
		if self.love > self.MAX_LOVE: self.love = self.MAX_LOVE
		t = str((self.i, v, self.love))
		if not self.heart:
			self.heart = Heart(self.atlas, self)
			self.heart.setPos(100, -1, 100)
		self.heart.turn(v>0)
		#self.debug(t, 50)
		self.heart.setScale(self.heart_bs*(0.25+self.love))
		#cs = 0.5 + v
		#self.heart.setColorScale(cs,cs,cs,1)
		if self.love < -self.MAX_LOVE: self.die()

	def beat(self, task):
		if (self.state == self.DEAD): return task.done
		#self.colorScaleInterval(task.delayTime, ec, self.getColorScale()).start()
		return task.again

	def stroll(self, task):
		if (self.state == self.DEAD) or (not self._tstroll) or (not self._tmove):
			return task.done
		task.delayTime = 3+(rd.random()+5)
		self.objective = Vec3(rd.random()*self.w.tilemap.pw, self.getY(), rd.random()*self.w.tilemap.ph)
		left = (self.objective-self.getPos()).x<0
		#self.play(self.BL if left else self.BR)
		return task.again

	def move(self, task): #lol this could be done with a lerp
		#i hate to do this but tasks are giving me a headache
		if not (self._tstroll and self._tmove): return task.done
		dt = globalClock.getDt()
		speed = dt*self.sp
		pos = self.getPos()
		path = self.objective-pos
		#print "moving" , pos, self.objective, path
		f = speed/(path.length() or 1.0)
		path = pos+(path*f)
		yy = self.w.nY(path.z) #except for this
		self.setPos(path.x, yy, path.z)
		return task.cont

	def stopBeat(self):
		if self._tbeat:
			taskMgr.remove(self._tbeat)
			self._tbeat = None

	def stopStroll(self):
		if self._tmove:
			taskMgr.remove(self._tmove)
			self._tmove = None
		if self._tstroll:
			taskMgr.remove(self._tstroll)#should not execute
			self._tstroll = None

	def startStroll(self):
		self.stopStroll()
		self.objective = self.getPos()
		self._tstroll = taskMgr.doMethodLater(0.1, self.stroll, 'wstroll') #repeat on a regular basis
		self._tmove = taskMgr.add(self.move, 'wmove') #repeats each frame

	def die(self):
		self.w.remWhale(self)
		self.stopBeat()
		self.stopStroll()
		ipos = self.getPos()
		epos = ipos+Vec3(0, 0, 20)
		Sequence(
			LerpPosHprScaleInterval(self, 0.5, epos, (0,0,90), self.getScale()*1.5, blendType="easeIn"),
			LerpPosHprScaleInterval(self, 0.5, ipos, (0,0,180), self.getScale(), blendType="easeOut"),
			LerpColorInterval(self, 2, (0, 0, 0, 1)),
			Wait(3.0),
			LerpColorInterval(self, 2, (0, 0, 0, 0)),
			Func(self.remove)
		).start()
