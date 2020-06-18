# -*- coding: utf-8 -*-
"""
This module allows to load tilemaps.
It is meant to be used with Tiled (www.mapeditor.org/).
Set the map to store the data as xml (on Map->Map properties)

"""

import itertools

from pandac.PandaModules import Vec4, Vec3, Vec2, Texture
from pandac.PandaModules import NodePath
from pandac.PandaModules import CardMaker
#from pandac.PandaModules import TextureStage
from xmlDao import Dao

"""
about padded textures:
		https://www.panda3d.org/manual/index.php/Choosing_a_Texture_Size
Instead, panda pads the data.
Panda creates a 1024x512 texture,
which is the smallest power-of-two size that can hold a 640x480 movie.
It sticks the 640x480 movie into the lower-left corner of the texture.
Then, it adds a black border to the right edge and top edge of the movie, padding it out to 1024x512.
careful with paddings, try to use 1024x1024 textures
"""
#TODO fix problem with tilesets that are padded (problem is with non-square textures)

def loadTMX(dir, file, parent):
	r = Dao('map', dir+'/'+file).root()
	tm = TileMap(parent)
	tm.dir = dir
	tm.file = file
	tmsize = map(int, [ getattr(r, at, 0)
		for at in ('width', 'height', 'tileheight', 'tilewidth') ])
	tm.setSize(*tmsize)
	#load the tilesets
	#less "elegant", more understandable, more portable (more loaders can be written)
	#speed is (should be) not critical here
	tm.tilesets = {}
	for ts in getattr(r, 'tileset', []):
		fgid = int(ts.firstgid)
		if not hasattr(ts, "image"): continue# TODO read tile based on image collections
		img = ts.image[0]
		rts	= TileSet(ts.name, fgid)
		rts.loadTexture(dir+'/'+img.source, int(img.width), int(img.height))
		rts.genRects(int(ts.tilewidth), int(ts.tileheight))
		tm.tilesets[fgid] = rts

	#load layers
	lays = {}
	for i, l in enumerate(getattr(r, 'layer', [])):
		n = l.name
		w, h = map(int, [getattr(l, a, 0) for a in ('width', 'height')])
		rl = Layer(tm, n, w, h, i)
		#i use the grouper outside because some tile editors could be smart enough to store the data as a matrix
		tiles = tuple(grouper(map(int, [t.gid for t in l.data[0].tile]), w))
		rl.loadTiles(tiles)
		lays[n] = rl
	tm.layers = lays

	#load object layers
	objs = {}
	for i, og in enumerate(getattr(r, "objectgroup", [])):
		rol = OLayer()
		rol.i = i
		rol.name = og.name
		for a in ('width', 'height', 'visible'):
			setattr(rol, a, int(getattr(og, a, 0)))
		#rol.visible = bool(rol.visible)

		robjs = []
		for o in getattr(og, "object", []):
			rect = map(int, [getattr(o, a, 0) for a in ('x', 'y', 'width', 'height')])
			ro = Obj(getattr(o, 'name', ""), getattr(o, 'type', ''), tm.ph, *rect)
			robjs.append(ro)
		rol.objs = tuple(robjs)
		objs[rol.name] = rol
	tm.olayers = objs
	return tm

def grouper(iterable, n, fillvalue=None):
	"grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
	args = [iter(iterable)] * n
	return itertools.izip_longest(fillvalue=fillvalue, *args)

class Tile(NodePath):
	def __init__(self, texture, pos, rect, parent):
		#self.tw, self.th = map(float, (texture.getOrigFileXSize(), texture.getOrigFileYSize()))
		self.tw, self.th = map(float, (texture.getXSize(), texture.getYSize()))
		self.cm = CardMaker('spritesMaker')
		#read note on animated sprite
		self.x, self.y, self.z = pos#pixel coords
		self.ox, self.oy, self.w, self.h = rect#pixel coords
		self.cm.setFrame(self.x, self.x+self.w, self.z, self.z+self.h)
		self.cm.setHasUvs(True)
		#print "tile y", self.y
		#padx = texture.getPadXSize()
		pady = texture.getPadYSize()
		#print "pads", padx, pady
		self.oy += pady#or textures not power of 2.
		tx1 = self.ox / self.tw
		tx2 = (self.ox + self.w) / self.tw
		#y coords for oy is 0-up, y coords for text is 0-up so dont forget to do the conversion (th- ...)
		ty1 = (self.th - self.oy ) / self.th
		ty2 = (self.th - self.oy - self.h) / self.th

		pw, ph = 1.0/self.tw, 1.0/self.th #1 pixel
		hph = ph/2.0 #half pixel

		#ll , ur (acronims for LowerLeft and UpperRight?)
		# (nearest fails to show a fixed texture, it alternates between 1px up and down when it moves. so.. 0.5 px sounds ok
		self.cm.setUvRange( (tx1, ty2+hph), (tx2, ty1-hph))
		# ty2-hph  ty1-hph works for minified textures, ty2 ty1 works for magnified textures
		# to make it work for boths i need to crop it by 1px (half from top, half from bottom) (but crops 1 px)
		#+/- pw/ph contracts the texture 1 pixel because it shows some artifacts...

		#self.cm.setUvRange( (tx1, ty2), (tx2, ty1))
		#This is mamamamamammaaagic! (shaders my .py!)

		NodePath.__init__(self, self.cm.generate())
		self.setY(self.y)
		self.setTexture(texture, 1)
		#ts = TextureStage.getDefault()
		#using setUVRange we dont need to do this (actually equivalent (in apparent results))
		#self.setTexScale(ts, self.w/self.tw, self.h/self.th)
		#ofx = self.ox/self.tw
		#ofy = (self.oy+self.h)/self.th
		#self.setTexOffset(ts, ofx, -ofy)

		self.reparentTo(parent)
		self.setTransparency(True)
"""
(3:53:34) |Craig|: try computing the offsets and adding them to the vertex positions when you make the card, instead of moving the created cards
(3:54:55) |Craig|: meaning leave all the card nodes at 0,0,0 (or at least the same position)
(3:55:06) nande: ok, and how do i add to the vertexes?
(3:55:12) |Craig|: change the settings you create them with
(3:55:16) nande: node.getVertexs()?
(3:56:05) |Craig|: Use http://www.panda3d.org/reference/devel/python/classpanda3d.core.CardMaker.php#a7068b0af1591eaea69e8c79733cefe29
(3:56:29) |Craig|: I guess http://www.panda3d.org/reference/devel/python/classpanda3d.core.CardMaker.php#a6df5a5773c19ed5c162328804dda06d5 can do it auctually
(3:56:44) |Craig|: just adjust those numbers according to the card's intended location
(3:56:56) nande: and let position to 0,0,0?
(3:57:00) |Craig|: ya
(3:57:36) |Craig|: then all the vertexes should be specified in identical coordinate systems, which should avoid the issues of them rounding differently
"""
class Obj:
	def __init__(self, name="", type="", layerH=0, x=0, y=0, width=0, height=0):
		self.name = name
		self.type = type
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		if layerH:	self.y = layerH - self.y

class OLayer:
	i = 0
	name = ""
	width = 0
	heigth = 0
	visible = 0
	objects = tuple()

class Layer:
	def __init__(self, tilemap, name, width, heigth, i=0):
		self._tm = tilemap
		self.name = name
		self.width = width
		self.heigth = heigth
		self.i = i
		self.tiles = []
		self.objs = {}

	def loadTiles(self, tile_ids):
		#tiles should be a matrix, if its a list use grouper "tiles_ids = list(grouper(d['data'], self.width, 0))"
		#self.tiles = []
		# tiled orders the array so the firsts items are the one of the top, even it has +Y coords.. which makes it stupid, but visually simpler
		# i could get the map height in tiles and start counting on that and decreasing the Y, but i rather iterate the list inversely

		y = 0
		tw = self._tm.tilewidth
		th = self._tm.tileheight
		col_width = 5
		col_real_width = tw*col_width
		#create a vector of columns to allow for object culling http://www.panda3d.org/forums/viewtopic.php?p=26819#26819
		#it was easier to use rows, but rows are larger, and the movement will be more likely to be horizontal. so the culling is more efficient this way
		#(we could create groups but i dont feel like it now)
		#this is very inneficient, if we could iterate the columns instead of rows, maybe it will be more efficient
		cols = []
		for i in range(len(tile_ids[0])/col_width):
			col = self._tm.parent.attachNewNode("map_column%s"%i)
			col.setX(i*col_real_width)
			cols.append(col)
		#ioff = 1.0/(len(self.tiles_id) or 1.0)
		#print "ioff", ioff
		#+(ioff*i)
		pd = 1.0/self._tm.ph
		for row_id in reversed(tile_ids):
			#row = []
			for i, tid in enumerate(row_id):
				if i%col_width == 0:
					x = 0
				if tid:
					z = -(self.i)+(pd*(y+th))
					pos = Vec3(x, z, y)
					ts = self._tm.tileSet(tid)
					if not ts:
						print ("tile %i not found"%tid)
						continue
					rect = ts.tileRect(tid)
					sp = Tile(ts.texture, pos, rect, cols[i/col_width])
					#row.append(sp)
				x += tw
			#self.tiles.append(list(row))
			y += th
		#this improves performance! thanks thomasEgi you're so cool! ( http://www.panda3d.org/forums/viewtopic.php?p=24102#24102 )
		for col in cols:
			col.flattenStrong()

class TileSet():
	name = ""
	tilewidth = tileheight = width = height = imagewidth = imageheight = firstgid = 0
	texture = None
	def __init__(self, name, firstgid):
		self.name = name
		self.firstgid = firstgid

	def loadTexture(self, file, imageheight, imagewidth):
		self.file = file
		self.imageheight = imageheight
		self.imagewidth = imagewidth

		from panda2d import TXFILTER, ANI
		self.texture = loader.loadTexture(self.file)
		self.texture.setMinfilter(TXFILTER)
		self.texture.setMagfilter(TXFILTER)
		#self.texture.setMinfilter(Texture.FTNearest)
		#self.texture.setMagfilter(Texture.FTNearest)#important
		if ANI >1: self.texture.setAnisotropicDegree(ANI)

	def genRects(self, tw, th):
		self.tileheight = th
		self.tilewidth = tw
		self.width = self.imagewidth / self.tilewidth
		self.height = self.imageheight / self.tileheight
		self.rects = tuple([
			tuple([
				Vec4(j*self.tilewidth, i*self.tileheight, self.tilewidth, self.tileheight)
				for j in range(self.width)
			])
			for i in range(self.height)
		])

	def tileRect(self, idn):
		real_id = idn - self.firstgid
		i, j = divmod(real_id, self.width)
		#i+=2
		#j = real_id % self.width#divmod?
		#i = int(real_id / self.width)
		r = self.rects[i][j]
		#print ("tilerect", idn, self.firstgid, real_id, i, j, r)
		return r

class TileMap:
	width =	height = tilewidth = tileheight = 0
	tilesets = {}
	layers = {}
	parent = None
	def __init__(self, parent = None):
		self.parent = parent
		self.tilesets = {}
		self.layers = {}

	def setSize(self, width, height, tilewidth, tileheight):
		self.width = width
		self.height = height
		self.tilewidth = tilewidth
		self.tileheight = tileheight
		self.pw = self.width * self.tilewidth
		self.ph = self.height * self.tilewidth

	def tileSet(self, tid):
		ids = sorted(self.tilesets.keys(), reverse=True)
		ts = None
		for k in ids:
			if tid>=k:
				ts = self.tilesets[k]
				break
		return ts

	def tileRect(self, idn):
		ts = self.tileSet(idn)
		if ts:
			return ts.tileRect(idn)
		return None

class BitmapFont():
	def __init__(self, file, charSize=(16, 16)):
		self.texture = loader.loadTexture(dir+'/'+self.image)
		self.charW, self.charH = charSize
		self.tw, self.th = (texture.getOrigFileXSize(), texture.getOrigFileYSize())
		self.width, self.height = self.tw/self.charW, self.th/self.charH

	def getCharRect(self, row, column):
		real_id = idn - self.firstgid
		i = (row*self.width)+column #technically faster than divmod
		return self.rects[i]#technically faster than 2 indexing
