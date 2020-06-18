#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pandac.PandaModules import TextureStage
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionHandlerEvent, CollisionTraverser

#TODO get pseudo_y

class World(ShowBase):
	def __init__(self, width, height, parent=None, cam=None, bgColor=(0,0,0), title="Panda2D", fullscreen=False, debug=False):
		ShowBase.__init__(self)
		self.setBackgroundColor(*bgColor)
		self.width , self.height = width, height
		if parent is None:
			self.node = self.pixel2dp
			self.cam = self.cam2dp
			#self.cam.setZ(2)
		else:
			self.node = parent
			self.cam = cam

		self.cam_node = self.cam.node()

		self.ar = self.node.getScale()[0]
		print ("AR", self.ar)
		#reparent and resize suggested by cool rdb ( http://www.panda3d.org/forums/viewtopic.php?p=91395&sid=348d8b21e0f59043c6bfbcadb210a303#91395 )
		self.cam.reparentTo(self.node)
		cam_lens = self.cam_node.getLens()
		cam_lens.setFilmSize(width, height)
		cam_lens.setFilmOffset(width/2.0, height/2.0)
		#and works like a charm obviously :D
		self.node.setDepthTest(True, 0)
		self.node.setDepthWrite(True)# By Baribal_@#panda3d
		if debug:
			from panda3d.core import SceneGraphAnalyzerMeter
			self.meter = SceneGraphAnalyzerMeter('meter', self.node.node())
			self.meter.setupWindow(self.win)
			self.setFrameRateMeter(True)

		# test some points
		#   points = [(0,0), (screenWidth, 0), (screenWidth, screenHeight), (screenWidth/2.0, screenHeight/2.0), (0, screenHeight)]
		#   for pt in points:
		#      print '%s -> %s' % (pt, str(parent.getRelativePoint(screenNode, Vec3(pt[0], 0, pt[1]))))

		#return [self.node, self.origin]
		
	def setColls(self, with_in=True, with_out=True, with_again=False, show=False):
		self.ctrav = CollisionTraverser("2Dtraverser")
		if show: self.ctrav.showCollisions(self.node)
		self.ch = CollisionHandlerEvent()
		if with_in: self.ch.addInPattern('into-%in')
		if with_again: self.ch.addAgainPattern('again-%in')
		if with_out: self.ch.addOutPattern('outof-%in')
		taskMgr.add(self._tsk_traverse, "_tsk_traverse")
	
	def _tsk_traverse(self, task):
		self.ctrav.traverse(self.node)
		return task.cont
		
	def follow(self, node):
		#yeah importing here is bad, but i'm planning on removing this.
		from panda3d.core import CompassEffect
		#this works like a charm, but following a character needs more control over the offset and maybe some limits,
		# and faking speed movement for the camera, so maybe is best to have a task for it.
		# http://www.panda3d.org/forums/viewtopic.php?p=50905#50905
		# http://www.panda3d.org/forums/viewtopic.php?p=10968#10968
		self.cam.setEffect(CompassEffect.make(node, CompassEffect.PPos))

	def fakeZ(self, y, layer=0):
		return layer + (y/float(self.height))

	#TODO scene manager :B
