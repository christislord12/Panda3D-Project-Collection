# -*- coding: utf-8 -*-
import random as rd
rd.seed()

import panda2d.sprites
#from direct.showbase import DirectObject #input
from pandac.PandaModules import NodePath
from direct.interval.LerpInterval import LerpColorInterval, LerpHprScaleInterval, LerpPosHprScaleInterval, LerpPosInterval
from direct.interval.IntervalGlobal import Sequence

from pandac.PandaModules import Vec4, Vec3, Vec2

FOODS = ('rf_0_on', 'rf_1_on', 'rf_2_on', )
class Food (panda2d.sprites.AnimatedSprite):
	def __init__(self, atlas, node, real=True):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, 'food' )
		food = rd.choice(FOODS)
		self.setSprite(food)
		if real:
			self.setCollide()
		
class M(panda2d.sprites.AnimatedSprite):#NodePath):#panda2d.sprites.AnimatedSprite):
	sp = 100
	UP = DOWN = LEFT = RIGHT = False
	m = None
	to_left = False
	life = 2.0
	food = 0.0
	eu = 0.08
	MAX_FOOD = 10
	def __init__(self, atlas, node, sekai):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, 'M' )
		#NodePath.__init__(self, node.attachNewNode("M"))
		#self.atlas = atlas
		self.w = sekai
		self.foods = []
		#self.M = panda2d.sprites.AnimatedSprite(self.atlas, self, "M")
		#self.M.setCollide(owner=self)
		self.setCollide()
		self.STANDING_L = self.atlas.animIndex("stand_l")
		self.STANDING_R = self.atlas.animIndex("stand_r")
		self.WALKING_L = self.atlas.animIndex("walk_l")
		self.WALKING_R = self.atlas.animIndex("walk_r")
		self.setMyState(self.STANDING_R)
		self.setPos(30, 0, 60)
		self.setTask()
		self._tbeat = taskMgr.doMethodLater(1, self.beat, 'mbeat')
		
	def giveFood(self, b):
		if self.food <= 0:
			return False
		if(not b.feed()):
			return False
		self.food -= self.eu
		fs = self.food*self.MAX_FOOD
		l = len(self.foods)
		if fs<l:
			for i in range(int(l-fs)):
				if self.foods: self.foods.pop(-1).remove()
		return True
	
	def getFood(self, f):
		if self.food >= 1.0: return False
		self.food += self.eu
		fs = self.food*self.MAX_FOOD
		l = len(self.foods)
		if l<fs:
			for i in range(int(fs-l)):
				nf = Food(self.atlas, self)
				nf.setPos(5*(l+i), -4 , 15)
				nf.setScale(.7)
				self.foods.append(nf)
		return True
	
	def die(self):
		print ("game over?")
		self.w.died()
		self.UP = self.DOWN = self.LEFT = self.RIGHT = False
		self.setMyState(self.atlas.animIndex('M_dead'))
		#self.play(self.atlas.animIndex('M_dead'))
		ipos = self.getPos()
		epos = ipos+Vec3(0, 0, 20)
		Sequence(
			LerpPosHprScaleInterval(self, 0.5, epos, (0,0,90), 1.5, blendType="easeIn"),
			LerpPosHprScaleInterval(self, 0.5, ipos, (0,0,180), 1, blendType="easeOut"),
			LerpColorInterval(self, 2, (0, 0, 0, 1))
		).start()
		
	def beat(self, task):
		#task.delayTime += 1
		self.life -= 0.01
		#self.M.debug(self.life)
		if self.life <=0:
			self.die()
			self._tbeat = None
			return task.done
		else:
			l2 = self.life
			ec = Vec4(l2, l2, l2, 1.0)
			self.card.colorScaleInterval(task.delayTime, ec).start()
			return task.again
		
	def setMyState(self, nstate):### WARNING!! "setState" overrides a base method  panda3d.core.NodePath.NodePath
		if self.state == nstate: return
		self.play(nstate)

	def setTask(self):
		if self.m: return
		self.m = taskMgr.add(self.move, 'mmove')

	def move(self, task):
		dt = globalClock.getDt()
		dy = dx = 0
		if self.UP: dy = self.sp
		if self.DOWN: dy = -self.sp
		if self.LEFT: dx = -self.sp
		if self.RIGHT: dx = self.sp
		
		y = self.getZ()+dy*dt
		#yy = self.w.floor_y + (self.w.pd*y)
		yy = self.w.nY(y)
		self.setPos(self.getX()+dx*dt, yy, y)
		if (dx == dy == 0):
			self.m = None
			self.setMyState(self.to_left and self.STANDING_L or self.STANDING_R)
			return task.done
		else:
			self.setMyState(self.to_left and self.WALKING_L or self.WALKING_R)
		return task.cont
	
	def up(self, down):
		self.UP = down
		if down: self.setTask()
	def left(self, down):
		self.LEFT = down
		if down:
			self.setTask()
			self.to_left = not self.RIGHT #True
		elif self.RIGHT:
			self.to_left = False
	def right(self, down):
		self.RIGHT = down
		if down:
			self.setTask()
			self.to_left = False
		elif self.LEFT:
			self.to_left = True
	def down(self, down):
		self.DOWN = down
		if down: self.setTask()

class Heart(panda2d.sprites.AnimatedSprite):
	def __init__(self, atlas, node, broken=False):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node )
		self.B = self.atlas.animIndex(broken and "h2" or "h1")
		self.play(self.B)
	
class B(panda2d.sprites.AnimatedSprite):#NodePath):
	sp = 15
	protein = 9
	er = 0.01#energy requirements
	eu = 0.012#energy unit
	heu = 0.005#half of it
	s = 1.0 #simpathy
	h = 0.0 #hunger
	N = 0#normal
	H = 1#hungry
	D = 2#dying
	DD = 3#dead
	bstate = 0
	spsleep = spangry = None
	objective = Vec3(0,0,0)
	def __init__(self, atlas, node, world):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node, "b" )
		#NodePath.__init__(self, node.attachNewNode("BNP"))
		#self.a = atlas
		self.n = node
		self.w = world
		self.BL = self.atlas.animIndex("b_l")
		self.BR = self.atlas.animIndex("b_r")
		self.STILL = self.atlas.animIndex("b_dead")
		#self.b = panda2d.sprites.AnimatedSprite(self.a, self, "b")
		#self.b.play(rd.choice((self.BL, self.BR)))
		#self.b.setCollide(owner=self)
		self.play(rd.choice((self.BL, self.BR)))
		self.setCollide()
		
		self._tstroll = None
		self._tmove = None
		self._tbeat = taskMgr.doMethodLater(1, self.beat, 'bbeat')

	def move(self, task):
		#i hate to do this but tasks are giving me a headache
		if not (self._tstroll and self._tmove): return task.done
		dt = globalClock.getDt()
		speed = dt*self.sp
		pos = self.getPos()
		path = self.objective-pos
		#print "moving" , pos, self.objective, path
		f = speed/(path.length() or 1.0)
		path = pos+(path*f)
		yy = self.w.nY(path.z)
		self.setPos(path.x, yy, path.z)
		return task.cont

	def stroll(self, task):
		if (self.bstate == self.DD) or (not self._tstroll) or (not self._tmove):
			return task.done
		task.delayTime = 2+(rd.random()+3)
		self.objective = Vec3(rd.random()*self.w.tilemap.pw, self.getY(), rd.random()*self.w.tilemap.ph)
		left = (self.objective-self.getPos()).x<0
		self.play(self.BL if left else self.BR)
		return task.again
		
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
		self._tstroll = taskMgr.doMethodLater(0.1, self.stroll, 'bstroll')
		self._tmove = taskMgr.add(self.move, 'bmove')

	def feed(self):
		if (self.bstate == self.DD) or (self.h <=0):#dead or full
			return False
		self.h -= self.protein*self.eu
		return True
	
	def die(self):
		self.h = 1.0
		self.bstate = self.DD
		self.setAngry(False)
		self.setSleep(False)
		self.stopBeat()
		self.stopStroll()
		self.s = -1
		self.play(self.STILL)
		ipos = self.getPos()
		epos = ipos+Vec3(0, 0, 20)
		Sequence(
			LerpPosHprScaleInterval(self, 0.5, epos, (0,0,90), 1.5, blendType="easeIn"),
			LerpPosHprScaleInterval(self, 0.5, ipos, (0,0,180), 1, blendType="easeOut"),
			LerpColorInterval(self, 2, (0, 0, 0, 1))
		).start()
			
	def setAngry(self, isit):
		if isit:
			if not self.spangry:
				self.spangry = panda2d.sprites.AnimatedSprite(self.atlas, self)
				self.spangry.play(self.atlas.animIndex("angry"))
				self.spangry.setPos(10, -0.001, 10)
		else:
			if self.spangry:
				self.spangry.remove()
				self.spangry = None
				
	def setSleep(self, isit):
		if isit:
			if not self.spsleep:
				self.play(self.STILL)
				self.stopStroll()
				self.spsleep = panda2d.sprites.AnimatedSprite(self.atlas, self)
				self.spsleep.play(self.atlas.animIndex("sleepy"))
				self.spsleep.setPos(10, -0.001, 10)
				self.colorScaleInterval(1, (1.0, 1.0, 1.0, 1.0)).start()
		else:
			if self.spsleep:
				self.spsleep.remove()
				self.spsleep = None
				self.play(self.BR)
				self.startStroll()
				
	def beat(self, task):
		if (self.bstate == self.DD): return task.done

		self.h += self.er + (rd.random()*self.er)
		hltz = self.h<0.20
		hgta = self.h>0.5

		#hgtd = self.h>=1.0
		if self.h>=1.0:
			self.die()
			return task.done
		elif hltz:
			self.s += self.heu
		else:
			self.s -= self.heu
			if (hgta):
				self.s -= self.eu #notice this adds to the other
			ec = (1.0, 1.0-(self.h*0.9), 1.0-(self.h*0.8), 1.0)
			self.colorScaleInterval(task.delayTime, ec, self.getColorScale()).start()
		self.setAngry(hgta)
		self.setSleep(hltz)
		#self.debug("%.4f\n%.4f"%(self.s, self.h))
		self.s = min(1, max(0, self.s))#clamp
		return task.again

	def onMDead(self, M):
		self.stopBeat()
		
		n = self
		#self.node().setCenter(Point3(0, -5, 0))
		if(self.s>0.5):
			h = Heart(self.atlas, n, True)
			h.setPos(-10, -0.1, 10)
			self.stopStroll()
			self.setSleep(False)
			self.setAngry(False)
			self.play(self.STILL)
			self.colorScaleInterval(3, (0.3, 0.3, 0.8, 1.0)).start()
			p = M.getPos()+Vec3(rd.random()*50, 0, rd.random()*50)
			p.y = self.w.floor_y + (self.w.pd*p.z)
			l = (self.getPos()-p).length()
			dur = l/self.sp
			self.objective = p
			LerpPosInterval(self, dur, p, blendType="easeOut").start()

			#self.addChild(h, (-10, -100, 10))
		#h.setScale(20000)
		#h.ls()
		#self.h = h
		#from panda3d.core import CompassEffect
		#h.setEffect(CompassEffect.make(self, CompassEffect.PPos))
		#self.setDepthTest(True, 0)
		#self.setDepthWrite(True)# By Baribal_@#panda3d
		#h.setPos(self.getPos()+Vec3(100, -100, 100))
