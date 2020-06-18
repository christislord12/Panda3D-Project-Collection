from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject

from scrolllist import *

import os

class FileBrowser:
	def __init__(self, pos = Point3(0,0,0)):
		#initializing everything
		self.xPadding = 5
		self.yPadding = 5
		self.currentPath = os.getcwd()+"\dataset"
		self.buttonNode = render2d.attachNewNode("buttonNode")
		self.buttonNode.setPos(pos)
		#create file list and update position
		self.fileList = ScrollList(self.buttonNode, 3)
		self.updatePosition()
		
		#build file list
		self.showFileList()
		
		#hide all by default
		self.hide()
	
	def showFileList(self):
		
		#add some sort of menu scroll or background
		
		files = os.listdir(self.currentPath)
		i = 1
		
		for file in files:
			parts = file.split(".")
			#if is a directory ignore and continue with the next step
			if parts[0] == file:
				continue
			else:
				ext = parts[len(parts)-1]
				#show only egg and bam objects
				if ext != "egg" and ext != "bam":
					continue
				b = DirectButton(text=file, text_fg=(1,1,1,1),frameColor=(0,0,0,0),text_align=TextNode.ALeft, suppressMouse = False)
				b.setScale(0.05)
				b["command"] = myObjectManager.addObject
				b["extraArgs"] = [file]
				self.fileList.addItem(b)
		
		self.updatePosition()
		
	def updatePosition(self):
		self.fileList.updatePosition()
	
	def show(self):
		self.fileList.show()
	
	def hide(self):
		self.fileList.hide()
