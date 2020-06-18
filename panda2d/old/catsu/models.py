# -*- coding: utf-8 -*-
import math
import panda2d.sprites

class Cat(panda2d.sprites.AnimatedSprite):
	def __init__(self, atlas, node):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node )
		self.WALKING = self.atlas.animIndex("cat_walking")
		self.HIT = self.atlas.animIndex("cat_hit")
		self.JUMPING = self.atlas.animIndex("cat_jump")
		self.play(self.WALKING)
		self.setPos(30, 0, 60)
		self.m = taskMgr.add(self.move, 'cat move')

	def move (self, task):
		#todo use lerp
		dt = globalClock.getDt()
		self.setX(self.getX()+40*dt)
		return task.cont

class Ghost(panda2d.sprites.AnimatedSprite):
	def __init__(self, atlas, node):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node )
		self.WALKING = self.atlas.animIndex("ghost")
		self.play(self.WALKING)
		self.setPos(300, 0, 100)
		self.a = 0
		self.ltask = taskMgr.add(self.lefttask, 'ghost-left')
		self.mtask = taskMgr.add(self.move, 'ghost-move')

	def move(self, task):
		nz = self.getZ()+(math.cos(self.a)*0.2)
		self.setZ(nz)
		self.a+=1*globalClock.getDt()
		return task.cont

	def lefttask(self, task):
		nx = self.getX()-(20*globalClock.getDt())
		if nx > 30:
			self.setX(nx)
			return task.cont
		else:
			self.stop()
			taskMgr.remove(self.mtask)
			return task.done


class Blast(panda2d.sprites.AnimatedSprite):
	def __init__(self, atlas, node):
		panda2d.sprites.AnimatedSprite.__init__(self, atlas, node )
		self.setPos(300, 0, 300)
		self.NORMAL = self.atlas.animIndex("Blast")
		self.play(self.NORMAL)
