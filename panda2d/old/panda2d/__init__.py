# -*- coding: utf-8 -*-
#import direct.directbase.DirectStart #da el render
#from direct.showbase.DirectObject import DirectObject
from panda3d.core import ConfigVariableString
ConfigVariableString('preload-textures', '0')
ConfigVariableString('preload-simple-textures', '1')
ConfigVariableString('texture-compression', '1')
ConfigVariableString('allow-incomplete-render', '1' )

from pandac.PandaModules import TextureStage
from direct.showbase.ShowBase import ShowBase

""" para saber si tenemos threads"""
#from pandac.PandaModules import Thread
#print "threads? ", Thread.isThreadingSupported()

class World(ShowBase):
	def __init__(self, width, height, parent=None, cam=None, bgColor=(0,0,0), debug=False):
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
		print "AR", self.ar
		#reparent and resize suggested by cool rdb ( http://www.panda3d.org/forums/viewtopic.php?p=91395&sid=348d8b21e0f59043c6bfbcadb210a303#91395 )
		self.cam.reparentTo(self.node)
		cam_lens = self.cam_node.getLens()
		cam_lens.setFilmSize(width, height)
		cam_lens.setFilmOffset(width/2.0, height/2.0)
		#and works like a charm obviously :D

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
	def follow(self, node):
		#yeah importing here is bad, but i'm planning on removing this.
		from panda3d.core import CompassEffect
		#this works like a charm, but following a character needs more control over the offset and maybe some limits,
		# and faking speed movement for the camera, so maybe is best to have a task for it.
		# http://www.panda3d.org/forums/viewtopic.php?p=50905#50905
		# http://www.panda3d.org/forums/viewtopic.php?p=10968#10968
		self.cam.setEffect(CompassEffect.make(node, CompassEffect.PPos))

