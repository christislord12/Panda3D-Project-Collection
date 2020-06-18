# -*- coding: utf-8 -*-
#Copyright 2015 Jerónimo Barraco Mármol - moongate.com.ar GPLv3 moongate.com.ar
#This is under development, but is quite usable,
#add comments at/suggestions whatnot here https://www.panda3d.org/forums/viewtopic.php?f=1&t=15500&p=91380
#help with the code here https://bitbucket.org/jerobarraco/panda2d
#chat here #panda3d @ irc.freenode.net

#DONE padded textures
#DONE MeshDrawer optional interchangeable: not needed
#DONE make a loader for sprites like the one for tiles
#TODO support animations with more than one sprite
#DONE go back to the animatedSprite in the same node
#DONE parse the tmx file directly even xml sucks


#import direct.directbase.DirectStart #da el render
#from direct.showbase.DirectObject import DirectObject
from panda3d.core import ConfigVariableString
ConfigVariableString('preload-textures', '0')
ConfigVariableString('preload-simple-textures', '1')
ConfigVariableString('texture-compression', '1')
ConfigVariableString('allow-incomplete-render', '1' )
#ConfigVariableString('textures-power-2', 'pad')#makes panda pad non-p2-sizes instead of downscaling

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "textures-power-2 pad")#makes panda pad non-p2-sizes instead of downscaling

from pandac.PandaModules import Texture #Vec4, Vec3, Vec2, Texture

TXFILTERS = (Texture.FTNearest, Texture.FTLinear, Texture.FTNearestMipmapNearest, Texture.FTLinearMipmapNearest, Texture.FTNearestMipmapLinear, Texture.FTLinearMipmapLinear )
TXFILTER = TXFILTERS[0]
ANI = 1

def setUp(width=640, height=480, title='Panda2D', fullscreen=False, origin=(50,50), txfilter=0, ani=1, keep_ar=True, wantTK=False):
	"""Very important function. Sets up the config. Call it before importing anything else from panda2d, especially the world"""
	global TXFILTER, ANI
	TXFILTER = TXFILTERS[txfilter]
	ANI = ani
	loadPrcFileData("", "win-size %s %s" % (width, height))
	loadPrcFileData("", "window-title %s"%title)
	loadPrcFileData("", "fullscreen %s"%(fullscreen and 1 or 0)) # Set to 1 for fullscreen
	loadPrcFileData("", "win-origin %s %s"%origin)
	if keep_ar:
		loadPrcFileData("", "aspect-ratio %s"%(width/float(height)))
	if wantTK:
		loadPrcFileData("", "want-directtools #t")
		loadPrcFileData("", "want-tk #t")

""" para saber si tenemos threads"""
#from pandac.PandaModules import Thread
#print "threads? ", Thread.isThreadingSupported()
