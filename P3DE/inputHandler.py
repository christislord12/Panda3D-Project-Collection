from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class InputHandler(DirectObject):
	def __init__(self):
		#ballancer
		self.scrollSpeed = 2
		#moving camera vars
		self.pressedS = False
		self.pressedX = False
		self.pressedY = False
		self.pressedZ = False
		self.pressedH = False
		self.pressedP = False
		self.pressedR = False
		self.pressedL = False
		self.pressedD = False
		self.pressedA = False
		#setting it active by default
		self.setActive()
		self.oldCoo = []
	
	def modObjects(self,task):
		dt = globalClock.getDt()
		
		#resolving L event
		if self.pressedL == True:
			if self.pressedP == True:
				#this is to avoid flood of requests
				#aka the user has to -up the key and then to press it again in order to do an other request
				print "INFO: creating new point light"
				myObjectManager.addPointLight()
				self.pressedP = False
			
			if self.pressedD == True:
				print "INFO: creating new directional light"
				self.pressedD = False
			
			if self.pressedA == True:
				print "INFO: creating new ambient light"
				self.pressedA = False
		
			dt = globalClock.getDt()
		
		#resolving S event
		if self.pressedS == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					if obj.getType() == "StaticObject":
						obj.getModel().setScale(obj.getModel().getScale()+((x-300)*0.01))
					if obj.getType() == "PointLightObject":
						att = obj.getPandaNode().getAttenuation()
						c1 = att.getX()+(x-300)*0.01
						c2 = att.getY()+(x-300)*0.01
						c3 = att.getZ()+(x-300)*0.01
						# Attenuation must be between 0 and 1
						if c1 < 0:
							c1 = 0
						if c2 < 0:
							c2 = 0
						if c3 < 0:
							c3 = 0
						
						p3 = Point3(c1,c2,c3)
						obj.getPandaNode().setAttenuation(p3)
		
		#resolving X event
		if self.pressedX == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					obj.getModel().setX(obj.getModel().getX()+((x-300)*0.01))
		
		#resolving Y event
		if self.pressedY == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					obj.getModel().setY(obj.getModel().getY()+((x-300)*0.01))
		
		#resolving Z event
		if self.pressedZ == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					obj.getModel().setZ(obj.getModel().getZ()+((x-300)*0.01))
		
		#resolving H event
		if self.pressedH == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					obj.getModel().setH(obj.getModel().getH()+((x-300)*0.1))
		
		#resolving P event
		if self.pressedP == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					obj.getModel().setP(obj.getModel().getP()+((x-300)*0.1))
		
		#resolving R event
		if self.pressedR == True:
			# figure out how much the mouse has moved (in pixels)
			md = base.win.getPointer(0)
			x = md.getX()
			y = md.getY()
			if base.win.movePointer(0, 300, 300):
				for obj in self.objList:
					obj.getModel().setR(obj.getModel().getR()+((x-300)*0.1))
		
		return Task.cont
	
	def setInactive(self):
		# Main Modifier
		self.ignoreAll()
		taskMgr.remove("objectModifierTask")
	
	def setActive(self):
		#custom events
		self.accept("e", myObjectManager.removeSelectedObjects)
		self.accept("f12", myApp.exportScene)
		
		# Main Modifier
		self.accept("s", self.pressKey, ["s"])
		self.accept("s-up", self.releaseKey, ["s"])
		self.accept("x", self.pressKey, ["x"])
		self.accept("x-up", self.releaseKey, ["x"])
		self.accept("y", self.pressKey, ["y"])
		self.accept("y-up", self.releaseKey, ["y"])
		self.accept("z", self.pressKey, ["z"])
		self.accept("z-up", self.releaseKey, ["z"])
		self.accept("h", self.pressKey, ["h"])
		self.accept("h-up", self.releaseKey, ["h"])
		self.accept("p", self.pressKey, ["p"])
		self.accept("p-up", self.releaseKey, ["p"])
		self.accept("r", self.pressKey, ["r"])
		self.accept("r-up", self.releaseKey, ["r"])
		self.accept("l", self.pressKey, ["l"])
		self.accept("l-up", self.releaseKey, ["l"])
		self.accept("d", self.pressKey, ["d"])
		self.accept("d-up", self.releaseKey, ["d"])
		self.accept("a", self.pressKey, ["a"])
		self.accept("a-up", self.releaseKey, ["a"])
		#self.ignore()
		taskMgr.add(self.modObjects, "objectModifierTask")
	
	def releaseKey(self,key):
		myCamera.mm.showMouse()
		#restoring old coo and emptying list
		
		#avoiding crash if someone click outside window
		if base.mouseWatcherNode.hasMouse():
			base.win.movePointer(0, self.oldCoo[0], self.oldCoo[1])
		oldCoo = []
		if key == "s":
			self.pressedS = False
		if key == "x":
			self.pressedX = False
		if key == "y":
			self.pressedY = False
		if key == "z":
			self.pressedZ = False
		if key == "h":
			self.pressedH = False
		if key == "p":
			self.pressedP = False
		if key == "r":
			self.pressedR = False
		if key == "l":
			self.pressedL = False
		if key == "d":
			self.pressedD = False
		if key == "a":
			self.pressedA = False
	
	def calcUnlockedObjects(self):
		print"DEBUG: calculating all unlocked objects"
		objList = myCamera.getSelectionTool().listSelected
		unlockedObjList = []
		for obj in objList:
			if obj.getLocking() == False:
				unlockedObjList.append(obj)
		return unlockedObjList
	
	def pressKey(self,key):
		myCamera.mm.hidMouse()
		#lulz system to restore old mouse coordinates after objects modifying
		md = base.win.getPointer(0)
		self.oldCoo = [md.getX(),md.getY()]
		base.win.movePointer(0, 300, 300)
		
		#refreshing unlocked object list
		self.objList = self.calcUnlockedObjects()
		
		if key == "s":
			self.pressedS = True
		if key == "x":
			self.pressedX = True
		if key == "y":
			self.pressedY = True
		if key == "z":
			self.pressedZ = True
		if key == "h":
			self.pressedH = True
		if key == "p":
			self.pressedP = True
		if key == "r":
			self.pressedR = True
		if key == "l":
			self.pressedL = True
		if key == "d":
			self.pressedD = True
		if key == "a":
			self.pressedA = True