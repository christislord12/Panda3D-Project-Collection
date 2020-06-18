# -*- coding: utf-8 -*-
#Copyright 2015 Jerónimo Barraco Mármol - moongate.com.ar GPLv3 moongate.com.ar
"""Example game made in 1 day for the global game jam 2015. It is rushed, not academic.
"""
##TODO feed the deads
##TODO life
##TODO get pseudo Z (Y)
##TODO food Y
##TODO aspect ratio


import random as rd
rd.seed()

#from pandac.PandaModules import loadPrcFileData
from panda3d.core import TextNode
size = width, height = 640, 480

import panda2d
#Before importing the world we need to set up stuff. 
panda2d.setUp(size[0], size[1], "77", False, (100, 100), txfilter=0, ani=0, keep_ar=True)

import panda2d.world
import panda2d.sprites
import panda2d.tiles

import m.models

class Mundo(panda2d.world.World):
	floor_y = -1
	def __init__(self):
		panda2d.world.World.__init__(self, size[0], size[1], bgColor=(100, 0, 100), debug=False)
		self.bs = []
		self.food = []
		self.zone_food = (20,20,20,20)
		self.addSprites()
		self.pkevs =  (
			('arrow_up', self.m.up),
			('arrow_left', self.m.left),
			('arrow_right', self.m.right),
			('arrow_down', self.m.down),
		)
		self.evs = self.pkevs + tuple()
		self.setKeys()
		self._tfood = taskMgr.doMethodLater(1+(rd.random()*2), self.addFood, 'wfood')
		self.setCollissions()
		
	def setCollissions(self):
		self.setColls(with_again=True)
		self.ctrav.addCollider(self.m.cnodep, self.ch)
		self.accept('into-CNfood', self.hColFood)
		self.accept('into-CNb', self.hColb)
		self.accept('again-CNb', self.hColb)
		return 
		
	def hColFood(self, data):
		food = data.getIntoNode().getPythonTag('owner')
		if self.m.getFood(food):
			food.removeNode()
	
	def hColb(self, data):
		b = data.getIntoNode().getPythonTag('owner')
		self.m.giveFood(b)
		
	def addFood(self, task):
		nf = m.models.Food(self.atlas, self.node)
		x, y, w, h = self.zone_food
		nfx = x+(rd.random()*w)
		nfy = y-(rd.random()*h)
		z = self.fakeZ(nfy, self.floor_y)
		nf.setPos(nfx, z, nfy)
		task.delayTime = 0.7+(rd.random()*1)
		return task.again
	
	def setKeys(self):
		for k, f in self.evs:
			self.accept(k, f, [True,])
			self.accept(k+'-up', f, [False,])
			
	def unsetPKeys(self):
		for k,f in self.pkevs:
			self.ignore(k)
			self.ignore(k+'-up')

	def died(self):
		self.unsetPKeys()
		if self._tfood:
			taskMgr.remove(self._tfood)
			self._tfood = None
		text = TextNode('node name')
		text.setText("Game Over?")
		text.setTextColor(1, 0.5, 0.5, 1)
		#text.setShadow(0.05, 0.05)
		#text.setShadowColor(0, 0, 0, 1.0)
		textNodePath = self.node.attachNewNode(text)
		textNodePath.colorScaleInterval(3, (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0)).start()
		textNodePath.setPos(10, -200, 10)
		textNodePath.setScale(70)
		for b in self.bs:
			b.onMDead(self.m)
		
	def addSprites(self):
		self.atlas = panda2d.sprites.Atlas()
		self.atlas.loadXml("m/data", fanim="anim.anim")
		self.tilemap = panda2d.tiles.loadTMX("m/data", "l1.tmx", self.node)
		self.pd = 1.0/(self.tilemap.ph or 1.0)
		#print "pixel density", self.pd
		self.m = None
		self.bs = []
		lob = self.tilemap.olayers['pjs']
		#self.floor_y = -lob.i
		#self.floor_y = -1
		self.floor_y = -self.tilemap.layers['ipj'].i
		for i, o in enumerate(lob.objs):
			pos = (o.x, -lob.i, o.y)
			if o.type == 'M':
				self.m = m.models.M(self.atlas, self.node, self)
				self.m.setPos(*pos)
				#print pos
			elif o.type == 'b':
				b = m.models.B(self.atlas, self.node, self)
				b.setPos(*pos)
				self.bs.append(b)
			elif o.type == 'zone_food':
				self.zone_food = (o.x, o.y, o.width, o.height)

	def nY(self, ny):
		return self.fakeZ(ny, self.floor_y)

def runWorld():
	world = Mundo()
	world.run()
