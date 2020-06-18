# -*- coding: utf-8 -*-
import json
import direct.task.TaskManagerGlobal

from pandac.PandaModules import Vec4, Vec3, Vec2, Texture
from panda3d.core import MeshDrawer

import itertools
import panda2d.sprites

def grouper(iterable, n, fillvalue=None):
	"grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
	args = [iter(iterable)] * n
	return itertools.izip_longest(fillvalue=fillvalue, *args)

class Layer:
	def __init__(self, d, tilemap):
		for at in ('width', 'height', 'x', 'y', 'visible', 'name', 'opacity'):
			setattr(self, at, d[at])
		self.layer_type = d['type']
		self.tilemap = self.layer_type == 'tilelayer'
		self.cam = tilemap.cam
		self.parent = tilemap.parent
		self.color = Vec4(1,1,1,1)#rgba?
		self.depth = 0
		self.m  = MeshDrawer()
		self.m.setBudget(1000)
		self.r = self.m.getRoot()
		self.r.setDepthWrite(False)
		self.r.setTransparency(True)
		self.r.reparentTo(self.parent)
		#self.r.setTwoSided(True)
		#self.r.setBin("fixed",0)

		if self.tilemap :
			self.loadTiles(d, tilemap)

	def loadTiles(self, d, tilemap):
		self.tiles_id = list(grouper(d['data'], self.width, 0))
		y = 0
		self.tiles = []
		# tiled orders the array so the firsts items are the one of the top, even it has +Y coords.. which makes it stupid, but visually simpler
		# i could get the map height in tiles and start counting on that and decreasing the Y, but i rather iterate the list inversely
		tw = tilemap.tilewidth
		th = tilemap.tileheight
		scale = tw/2.0#i have no idea why /2......
		self.texture = None
		for row_id in reversed(self.tiles_id):
			row = []
			x = 0
			for  tile_id in (row_id):
				if tile_id:
					pos = Vec3(x, self.depth, y)
					ts = tilemap.tileSet(tile_id)
					rect = ts.tileRect(tile_id)
					if self.texture is None:
						self.texture = ts.texture
					#self.m.billboard((50, 0, 50), (0, 0, 1, 1) , 10,  (1,1,1,1))#rgbA
					bill = (pos, rect, scale, self.color)
					row.append(bill)
				x+= tw
			self.tiles.append(list(row))
			y += th

		self.tiles = list(self.tiles)
		self.r.setTexture(self.texture)
		direct.task.TaskManagerGlobal.taskMgr.add(self.draw , "draw-tilema-"+self.name)

	def draw(self, task):
		self.m.begin(self.cam, self.parent)
		#todo optimize this
		for row in self.tiles:
			for bill in row:
				#print bill
				self.m.billboard(*bill)
		self.m.end()
		return task.cont


class TileSet():
	def __init__(self, d, dir):
		for at in ('firstgid', 'image', 'imageheight', 'imagewidth', 'margin', 'name', 'spacing',
							 'tileheight', 'tilewidth', 'transparentcolor'):
			setattr(self, at, d.get(at, None))
		self.texture = loader.loadTexture(dir+'/'+self.image)
		self.texture.setMinfilter(Texture.FTLinearMipmapLinear)
		self.texture.setMagfilter(Texture.FTLinearMipmapLinear)
		self.width = self.imagewidth / self.tilewidth
		self.height = self.imageheight / self.tileheight
		w = 1.0/self.width
		h = 1.0/self.height
		#Vec4 coordinates starts counting from the bottom left, counting to the top right.
		# If you had a 16x16 plate, the 15th field in the 11th row would be:
		# Vec4(14.0/16,5.0/16,1.0/16,1.0/16.)
		self.rects = list([
			list([
				#Vec4(j*w, i*h, w, h)
				Vec4(j*w, i*h, w, h)
				#Vec4(0,0,1,1) #Frame of Vec4(0,0,1,1) would be the entire texture
				#Vec4(j*tw, i*th, tw, th)
				for j in range(self.width)
			])
			for i in range(self.height-1, -1, -1)
		])

	def tileRect(self, idn):
		real_id = idn - self.firstgid
		j = real_id % self.width
		i = int(real_id / self.width)
		return self.rects[i][j]

class TileMap:
	def __init__(self, dir, file, parent, cam):
		self.parent = parent
		self.cam = cam
		self.js = json.load(open(dir+'/'+file, 'r'))
		for at in ('width', 'height', 'tileheight', 'tilewidth'):
			setattr(self, at, self.js[at])

		self.tilesets = { ts['firstgid']:TileSet(ts, dir) for ts in self.js['tilesets'] }
		self.layers = [Layer(l, self) for l in self.js['layers']]


	def tileSet(self, tid):
		ids = sorted(self.tilesets.keys(), reverse = True)
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
