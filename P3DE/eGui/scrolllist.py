from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject

from utilities import *

class ScrollList(DirectObject):
	def __init__(self,parent,size):
		#getting parent
		self.parent = parent
		#list for widgets
		self.widgets = []
		#view options
		#fixed just for now
		self.size = 10
		self.currentMin = 0
		self.currentMax = self.size
		#style
		self.lineSpacing = 0.1
		self.height = 0
		self.width = 0
		#main node for pos and ecc
		self.listNode = aspect2d.attachNewNode("listNode")
		self.updatePosition()
		
		#setting events management
		self.accept("wheel_up", self.scrollUp)
		self.accept("wheel_down", self.scrollDown)
	
	def updatePosition(self):
		self.listNode.setPos(Utilities.render2aspect(self.parent.getPos()))
	
	def update(self):
		#recomputing height and width
		self.computeWidth()
		self.computeHeight()
		#updating hidden/shown
		z = 0
		counter = 0
		for widget in self.widgets:
			widget.reparentTo(self.listNode)
			widget.setZ(self.listNode, z)
			z -= self.lineSpacing
			#counter things
			counter += 1
			widget.show()
			if counter <= self.currentMin:
				widget.hide()
				z += self.lineSpacing
			if counter > self.currentMax:
				#widget.hide()
				widget.reparentTo(hidden)
	
	def scrollDown(self):
		#some checks
		if len(self.widgets) <= self.currentMax:
			return
		if self.isMouseOver() == True:
			#mod the focused items in list
			self.currentMin += 1
			self.currentMax += 1
			#redraw everything
			self.update()
		
	
	def scrollUp(self):
		#some checks
		if self.currentMin == 0:
			return
		if self.isMouseOver() == True:
			#mod the focused items in list
			self.currentMin -= 1
			self.currentMax -= 1
			#redraw everything
			self.update()
		
	
	def show(self):
		self.listNode.show()
	
	def hide(self):
		self.listNode.hide()
	
	def setSize(self,i):
		self.size = i
		self.update()
	
	def addItem(self,item):
		self.widgets.append(item)
		self.update()
	
	def computeHeight(self):
		self.height = 0
		maxWidgets = 0
		for widget in self.widgets:
			self.height += widget.getHeight()*0.05
			maxWidgets += 1
			if maxWidgets == self.size:
				break
		self.height =+ self.lineSpacing*self.size
	
	def computeWidth(self):
		self.width = 0
		for widget in self.widgets:
			if widget.getWidth() > self.width:
				self.width = widget.getWidth()*0.05
	
	def isMouseOver(self):
		#function
		m = base.mouseWatcherNode.getMouse()
		x = m.getX()
		y = m.getY()
		
		#taken coordinates from parent because of render2d and not aspect2d
		#more compatible with mouse coordinates 
		xMod = self.parent.getX()
		yMod = self.parent.getZ()
		
		print xMod+self.width
		
		print yMod-self.height
		
		#check x
		if x > xMod and x < xMod+self.width:
			#check y
			if y < yMod and y > yMod-self.height:
				return True
				
		return False
