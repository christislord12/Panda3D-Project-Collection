# -*- coding: utf-8 -*-
import json
import itertools

from pandac.PandaModules import Vec4, Vec3, Vec2, Texture
from pandac.PandaModules import NodePath
from pandac.PandaModules import CardMaker
from pandac.PandaModules import TextureStage


def grouper(iterable, n, fillvalue=None):
	"grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
	args = [iter(iterable)] * n
	return itertools.izip_longest(fillvalue=fillvalue, *args)

class Tile(NodePath):
	def __init__(self, texture, pos, rect, parent):
		self.tw, self.th = map(float, (texture.getXSize(), texture.getYSize()))
		self.cm = CardMaker('spritesMaker')
		#read note on animated sprite
		self.x, self.y, self.z = pos#pixel coords
		self.ox, self.oy, self.w, self.h = rect#pixel coords

		self.cm.setFrame(self.x, self.x+self.w, self.z, self.z+self.h)
		self.cm.setHasUvs(True)

		tx1 = self.ox / self.tw
		tx2 = (self.ox + self.w) / self.tw
		#y coords for oy is 0-up, y coords for text is 0-up so dont forget to do the conversion (th- ...)
		ty1 = (self.th - self.oy ) / self.th
		ty2 = (self.th - self.oy - self.h) / self.th

		pw, ph = 1/self.tw, 1/self.th #1 pixel
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

class Layer:
	def __init__(self, d, tilemap):
		for at in ('width', 'height', 'x', 'y', 'visible', 'name', 'opacity'):
			setattr(self, at, d[at])
		self.layer_type = d['type']
		self.tilemap = self.layer_type== 'tilelayer'
		if self.tilemap :
			self.loadTiles(d, tilemap)

	def loadTiles(self, d, tilemap):
		self.tiles_id = list(grouper(d['data'], self.width, 0))
		y = 0
		self.tiles = []
		# tiled orders the array so the firsts items are the one of the top, even it has +Y coords.. which makes it stupid, but visually simpler
		# i could get the map height in tiles and start counting on that and decreasing the Y, but i rather iterate the list inversely

		#create a vector of columns to allow for object culling http://www.panda3d.org/forums/viewtopic.php?p=26819#26819
		#it was easier to use rows, but rows are larger, and the movement will be more likely to be horizontal. so the culling is more efficient this way
		#(we could create groups but i dont feel like it now)
		#this is very inneficient, if we could iterate the columns instead of rows, maybe it will be more efficient
		tw = tilemap.tilewidth
		col_width = 5
		col_real_width = tw*col_width
		cols = []
		for i in range(len(self.tiles_id [0])/col_width):
			col = tilemap.parent.attachNewNode("map_column%s"%i)
			col.setX(i*col_real_width)
			cols.append(col)

		for row_id in reversed(self.tiles_id):
			#row = []
			for i, tile_id in enumerate(row_id):
				if i%col_width == 0:
					x = 0
				if tile_id:

					pos = Vec3(x, 3, y)
					ts = tilemap.tileSet(tile_id)
					rect = ts.tileRect(tile_id)
					sp = Tile(ts.texture, pos, rect, cols[i/col_width])
					#row.append(sp)
				x+= tw

			#self.tiles.append(list(row))
			y += tilemap.tileheight
		#this improves performance! thanks thomasEgi you're so cool! ( http://www.panda3d.org/forums/viewtopic.php?p=24102#24102 )
		for col in cols:
			col.flattenStrong()

class TileSet():
	def __init__(self, d, dir):
		for at in ('firstgid', 'image', 'imageheight', 'imagewidth', 'margin', 'name', 'spacing',
							 'tileheight', 'tilewidth', 'transparentcolor'):
			setattr(self, at, d.get(at, None))
		self.texture = loader.loadTexture(dir+'/'+self.image)
		#self.texture.setMinfilter(Texture.FTLinearMipmapLinear)
		#self.texture.setMagfilter(Texture.FTLinearMipmapLinear)
		self.texture.setMinfilter(Texture.FTNearest)
		self.texture.setMagfilter(Texture.FTNearest)#important
		self.width = self.imagewidth / self.tilewidth
		self.height = self.imageheight / self.tileheight
		self.rects = list([
			list([
				Vec4(j*self.tilewidth, i*self.tileheight, self.tilewidth, self.tileheight)
				for j in range(self.width)
			])
			for i in range(self.height)
		])

	def tileRect(self, idn):
		real_id = idn - self.firstgid
		j = real_id % self.width#divmod?
		i = int(real_id / self.width)
		return self.rects[i][j]

class TileMap:
	def __init__(self, dir, file, parent):
		self.parent = parent
		self.js = json.load(open(dir+'/'+file, 'r'))
		for at in ('width', 'height', 'tileheight', 'tilewidth'):
			setattr(self, at, self.js[at])

		self.tilesets = { ts['firstgid']:TileSet(ts, dir) for ts in self.js['tilesets'] }
		self.layers = [Layer(l, self) for l in self.js['layers']]


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
		self.tw, self.th = (texture.getXSize(), texture.getYSize())
		self.width, self.height = self.tw/self.charW, self.th/self.charH

	def getCharRect(self, row, column):
		real_id = idn - self.firstgid
		i = (row*self.width)+column #technically faster than divmod
		return self.rects[i]#technically faster than 2 indexing
