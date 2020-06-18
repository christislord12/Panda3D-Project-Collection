#Move to world
from pandac.PandaModules import loadPrcFileData

size = width, height = 480, 320
loadPrcFileData("", "window-title test")
loadPrcFileData("", "fullscreen 0") # Set to 1 for fullscreen
loadPrcFileData("", "win-size %s %s" % (width, height))
loadPrcFileData("", "win-origin 10 10")
loadPrcFileData("", "textures-power-2 pad")#makes panda pad non-p2-sizes instead of downscaling

import panda2d_xml
import panda2d_xml.sprites

class Mundo(panda2d_xml.World):
	def __init__(self):
		panda2d_xml.World.__init__(self, size[0], size[1], bgColor=(100, 0,0), debug=True )
		self.addSprites()

	def addSprites(self):
		self.atlas = panda2d_xml.sprites.Atlas("data", fanim="newAnimation.anim")
		self.sp = self.atlas.newSprite('r6', self.node)
		self.sp.setPos(50.0, 50.0, 50.0)
		self.WALKING = self.atlas.animIndex("Animation")
		self.sp.play(self.WALKING)
#		class Cat(panda2d.sprites.AnimatedSprite):
#			def __init__(self, atlas, node):
#				panda2d.sprites.AnimatedSprite.__init__(self, atlas, node )
#				self.WALKING = self.atlas.animIndex("cat_walking")
#				self.HIT = self.atlas.animIndex("cat_hit")
#				self.JUMPING = self.atlas.animIndex("cat_jump")
#				self.play(self.WALKING)
#				self.setPos(30, 0, 60)
#				self.m = taskMgr.add(self.move, 'cat move')
#		pass



world = Mundo()
run()
