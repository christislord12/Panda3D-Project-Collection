from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

import libpanda
import math 

'''
This class is used to move camera WASD in FPS style
'''

class KeyboardMover(DirectObject):
	def __init__(self):
		#ballancer
		self.scrollSpeed = 2
		#moving camera vars
		self.pressedUp = False
		self.pressedDown = False
		self.pressedLeft = False
		self.pressedRight = False
		self.pressedFUp = False
		self.pressedFDown = False
		#setting up keys
		keys = ["w","s","a","d","t","g"]
		self.setupKeys(keys)
	
	def moveCamera(self,task):
		dt = globalClock.getDt()
		if self.pressedUp == True:
			camera.setY(camera, self.scrollSpeed*10*dt)
		if self.pressedDown == True:
			camera.setY(camera, -1*self.scrollSpeed*10*dt)
		if self.pressedLeft == True:
			camera.setX(camera, -1*self.scrollSpeed*10*dt)
		if self.pressedRight == True:
			camera.setX(camera, self.scrollSpeed*10*dt)
		if self.pressedFUp == True:
			camera.setZ(camera, self.scrollSpeed*10*dt)
		if self.pressedFDown == True:
			camera.setZ(camera, -1*self.scrollSpeed*10*dt)
		return Task.cont
	
	def setUnactive(self):
		self.ignoreAll()
		taskMgr.remove("keyboardMoverTask")
	
	def setActive(self):
		self.accept(self.up, self.pressKey, ["up"])
		self.accept(self.down, self.pressKey, ["down"])
		self.accept(self.left, self.pressKey, ["left"])
		self.accept(self.right, self.pressKey, ["right"])
		self.accept(self.FUp, self.pressKey, ["fup"])
		self.accept(self.FDown, self.pressKey, ["fdown"])
		self.accept(self.up+"-up", self.releaseKey, ["up"])
		self.accept(self.down+"-up", self.releaseKey, ["down"])
		self.accept(self.left+"-up", self.releaseKey, ["left"])
		self.accept(self.right+"-up", self.releaseKey, ["right"])
		self.accept(self.FUp+"-up", self.releaseKey, ["fup"])
		self.accept(self.FDown+"-up", self.releaseKey, ["fdown"])
		#self.ignore()
		taskMgr.add(self.moveCamera, "keyboardMoverTask")
	
	def releaseKey(self,key):
		if key == "up":
			self.pressedUp = False
		if key == "down":
			self.pressedDown = False
		if key == "left":
			self.pressedLeft = False
		if key == "right":
			self.pressedRight = False
		if key == "fup":
			self.pressedFUp = False
		if key == "fdown":
			self.pressedFDown = False
	
	def pressKey(self,key):
		if key == "up":
			self.pressedUp = True
		if key == "down":
			self.pressedDown = True
		if key == "left":
			self.pressedLeft = True
		if key == "right":
			self.pressedRight = True
		if key == "fup":
			self.pressedFUp = True
		if key == "fdown":
			self.pressedFDown = True
	
	def getKeys(self):
		keys = [self.up, self.down, self.left, self.right, self.FUp, self.FDown]
		return keys
	
	def setupKeys(self,keys):
		self.up = keys[0]
		self.down = keys[1]
		self.left = keys[2]
		self.right = keys[3]
		self.FUp = keys[4]
		self.FDown = keys[5]

'''
This class is use to move mouse when in FPS (fly) mode
setActive() -> used to activate FPS mouse slide
setUnactive() -> inactivate FPS behaviour
'''

class MouseMover(DirectObject):
	def __init__(self):
		#camera rotation settings
		self.heading = 0
		self.pitch = 0
		#used to restore last mouse position in editor
		self.lastCoo = []
	
	def flyCamera(self,task):
		# figure out how much the mouse has moved (in pixels)
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()
		if base.win.movePointer(0, 300, 300):
			self.heading = self.heading - (x - 300) * 0.1
			self.pitch = self.pitch - (y - 300) * 0.1
		if (self.pitch < -85): self.pitch = -85
		if (self.pitch >  85): self.pitch =  85
		base.camera.setH(self.heading)
		base.camera.setP(self.pitch)
		return Task.cont
	
	def hidMouse(self):
		#hiding mouse
		props = WindowProperties()
		props.setCursorHidden(True) 
		base.win.requestProperties(props)
	
	def showMouse(self):
		props = WindowProperties()
		props.setCursorHidden(False) 
		base.win.requestProperties(props)
		
	def setActive(self):
		#hiding mouse
		self.hidMouse()
		#storing infos
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()
		self.lastCoo = [x,y]
		#start activating this shit
		base.win.movePointer(0,300,300)
		taskMgr.add(self.flyCamera, "mouseMoverTask")
	
	def setUnactive(self):
		#showing mouse
		self.showMouse()
		#then removing task and resetting pointer to previous position
		taskMgr.remove("mouseMoverTask")
		base.win.movePointer(0,self.lastCoo[0],self.lastCoo[1])
		
class PropSet:
	def __init__(self):
		#fullscreen toggle
		self.full = False
		self.displayModes = []
		self.getSupportedDisplayRes()
	
	def getSupportedDisplayRes(self):
		di = base.pipe.getDisplayInformation()
		wp = WindowProperties()
		for index in range(di.getTotalDisplayModes()):
			if abs(float(di.getDisplayModeWidth(index)) / float(di.getDisplayModeHeight(index)) - (16. / 9.)) < 0.001:
				self.displayModes.append([di.getDisplayModeWidth(index), di.getDisplayModeHeight(index)])
	def setFullscreen(self,bool):
		wp = WindowProperties()
		if bool == False:
			wp.setSize(self.displayModes[0][0], self.displayModes[0][1])
			wp.setFullscreen(False)
			self.full = False
		else:
			wp.setSize(self.displayModes[len(self.displayModes) - 1][0], self.displayModes[len(self.displayModes) - 1][1])
			wp.setFullscreen(True)
			self.full = True
		base.win.requestProperties(wp)
                
	def toggleFullscreen(self):
		wp = WindowProperties()
		if self.full:
			wp.setSize(self.displayModes[0][0], self.displayModes[0][1])
			wp.setFullscreen(False)
			self.full = False
		else:
			wp.setSize(self.displayModes[len(self.displayModes) - 1][0], self.displayModes[len(self.displayModes) - 1][1])
			wp.setFullscreen(True)
			self.full = True
		base.win.requestProperties(wp)

class KeyboardModifiers(DirectObject): 
	def __init__(self): 
		self.booAlt = False 
		self.booControl = False 
		self.booShift = False 
		self.accept("alt", self.OnAltDown) 
		self.accept("alt-up", self.OnAltUp) 
		self.accept("control", self.OnControlDown) 
		self.accept("control-up", self.OnControlUp) 
		self.accept("shift", self.OnShiftDown) 
		self.accept("shift-up", self.OnShiftUp) 
	 
	def OnAltDown(self): 
		self.booAlt = True 
		
	def OnAltUp(self): 
		self.booAlt = False 
		
	def OnControlDown(self): 
		self.booControl = True 
	 
	def OnControlUp(self): 
		self.booControl = False 
		
	def OnShiftDown(self): 
		self.booShift = True 
		
	def OnShiftUp(self): 
		self.booShift = False 

class SelectionTool(DirectObject):
	def __init__(self, listConsideration=[]):
		#active and not
		self.active = True
		self.kmod = KeyboardModifiers()
		#Create a selection window using cardmaker
		#We will use the setScale function to dynamically scale the quad to the appropriate size in UpdateSelRect
		temp = CardMaker('')
		temp.setFrame(0, 1, 0, 1)
		#self.npSelRect is the actual selection rectangle that we dynamically hide/unhide and change size
		self.npSelRect = render2d.attachNewNode(temp.generate())
		self.npSelRect.setColor(1,1,0,.2)
		self.npSelRect.setTransparency(1)
		self.npSelRect.hide()
		LS = LineSegs()
		LS.moveTo(0,0,0)
		LS.drawTo(1,0,0)
		LS.drawTo(1,0,1)
		LS.drawTo(0,0,1)
		LS.drawTo(0,0,0)
		self.npSelRect.attachNewNode(LS.create())
		self.listConsideration = listConsideration
		self.listSelected = []
		self.listLastSelected = []
		
		self.pt2InitialMousePos = (-12, -12)
		self.pt2LastMousePos = (-12, -12)
		
		####----Used to differentiate between group selections and point selections
		#self.booMouseMoved  = False
		self.fFovh, self.fFovv = base.camLens.getFov()
		
		####--Used to control how frequently update_rect is updated;
		self.fTimeLastUpdateSelRect = 0
		self.fTimeLastUpdateSelected = 0
		self.UpdateTimeSelRect = 0.015
		self.UpdateTimeSelected = 0.015
		
		####------Register the left-mouse-button to start selecting
		self.accept("mouse1", self.OnStartSelect)
		self.accept("control-mouse1", self.OnStartSelect)
		self.accept("mouse1-up", self.OnStopSelect)
		self.taskUpdateSelRect = 0
	
	def removeObject(self,o):
		if o in self.listConsideration:
			self.listConsideration.remove(o)
		if o in self.listSelected:
			#execute deselection object
			self.funcDeselectActionOnObject(o)
			#get rid of it
			self.listSelected.remove(o)
		if o in self.listLastSelected:
			self.listLastSelected.remove(o)
	
	def appendObject(self,o):
		if o not in self.listConsideration:
			self.listConsideration.append(o)
	
	def setActive(self):
		self.active = True
	
	def setUnactive(self):
		self.active = False
	
	def TTest(self):
		print "hello control-mouse1"
	
	#functions executed when every object is selected
	def funcSelectActionOnObject(self, obj):
		obj.selectionEvent()
	
	#functions executed when every object is selected  
	def funcDeselectActionOnObject(self, obj):
		obj.deselectionEvent()
	
	def OnStartSelect(self):
		if not self.active:
			return
		if not base.mouseWatcherNode.hasMouse():
			return
		if base.mouseWatcherNode.getMouse().getX() > 0.4:
			return
		self.booMouseMoved = False
		self.booSelecting = True
		self.pt2InitialMousePos = Point2(base.mouseWatcherNode.getMouse())
		self.pt2LastMousePos = Point2(self.pt2InitialMousePos)
		self.npSelRect.setPos(self.pt2InitialMousePos[0], 1, self.pt2InitialMousePos[1])
		self.npSelRect.setScale(1e-3, 1, 1e-3)
		self.npSelRect.show()
		self.taskUpdateSelRect = taskMgr.add(self.UpdateSelRect, "UpdateSelRect")
		self.taskUpdateSelRect.lastMpos = None
		
	def OnStopSelect(self):
		if not self.active:
			return
		if not base.mouseWatcherNode.hasMouse():
			return
		if self.taskUpdateSelRect != 0:
			taskMgr.remove(self.taskUpdateSelRect)
		self.npSelRect.hide()
		self.booSelecting = False
		#If the mouse hasn't moved, it's a point selection
		if (abs(self.pt2InitialMousePos[0] - self.pt2LastMousePos[0]) <= .01) & (abs(self.pt2InitialMousePos[1] - self.pt2LastMousePos[1]) <= .01):
			objTempSelected = 0
			fTempObjDist = 2*(base.camLens.getFar())**2
			for i in self.listConsideration:
				if type(i.getModel()) != libpanda.NodePath:
					raise 'Unknown objtype in selection'
				else:
					sphBounds = i.getModel().getBounds()
					#p3 = base.cam.getRelativePoint(render, sphBounds.getCenter())
					p3 = base.cam.getRelativePoint(i.getModel().getParent(), sphBounds.getCenter())
					r = sphBounds.getRadius()
					screen_width = r/(p3[1]*math.tan(math.radians(self.fFovh/2)))
					screen_height = r/(p3[1]*math.tan(math.radians(self.fFovv/2)))
					p2 = Point2()
					base.camLens.project(p3, p2)
					#If the mouse pointer is in the "roughly" screen-projected bounding volume
					if (self.pt2InitialMousePos[0] >= (p2[0] - screen_width/2)):
						if (self.pt2InitialMousePos[0] <= (p2[0] + screen_width/2)):
							if (self.pt2InitialMousePos[1] >= (p2[1] - screen_height/2)):
								if (self.pt2InitialMousePos[1] <= (p2[1] + screen_height/2)):
									#We check the obj's distance to the camera and choose the closest one
									dist = p3[0]**2+p3[1]**2+p3[2]**2 - r**2
									if dist < fTempObjDist:
										fTempObjDist = dist
										objTempSelected = i

			if objTempSelected != 0:
				if self.kmod.booControl:
					self.listSelected.append(objTempSelected)
				else:
					for i in self.listSelected:
						self.funcDeselectActionOnObject(i)
				self.listSelected = [objTempSelected]
				self.funcSelectActionOnObject(objTempSelected)
			else:
				if base.mouseWatcherNode.getMouse().getX() > 0.4:
					return
				for i in self.listSelected[:]:
					self.funcDeselectActionOnObject(i)
					self.listSelected.remove(i)
		#after all this check gui changes needed
		
		if len(self.listSelected) > 1:
			# WRITE ME - not completed
			myGui.manyObjSelected()
		if len(self.listSelected) == 0:
			myGui.noneObjSelected()
		if len(self.listSelected) == 1:
			myGui.oneObjSelected()

	def UpdateSelRect(self, task): 
		if not self.active:
			return
		#Make sure we have the mouse 
		if not base.mouseWatcherNode.hasMouse(): 
			return Task.cont 
		mpos = base.mouseWatcherNode.getMouse() 
		t = globalClock.getRealTime() 
		#First check the mouse position is different 
		if self.pt2LastMousePos != mpos: 
			self.booMouseMoved = True 
			#We only need to check this function every once in a while 
			if (t - self.fTimeLastUpdateSelRect) > self.UpdateTimeSelRect: 
				self.fTimeLastUpdateSelRect =  t 
				self.pt2LastMousePos = Point2(mpos) 
				 
				#Update the selection rectange graphically 
				d = self.pt2LastMousePos - self.pt2InitialMousePos 
				self.npSelRect.setScale(d[0] if d[0] else 1e-3, 1, d[1] if d[1] else 1e-3) 
						
		if (abs(self.pt2InitialMousePos[0] - self.pt2LastMousePos[0]) > .01) & (abs(self.pt2InitialMousePos[1] - self.pt2LastMousePos[1]) > .01): 
			if (t - self.fTimeLastUpdateSelected) > self.UpdateTimeSelected: 
				#A better way to handle a large number of objects is to first transform the 2-d selection rect into 
				#its own view fustrum and then check the objects in world space. Adding space correlation/hashing 
				#will make it go faster. But I'm lazy. 
				self.fTimeLastUpdateSelected = t 
				self.listLastSelected = self.listSelected 
				self.listSelected = [] 
				#Get the bounds of the selection box 
				fMouse_Lx = min(self.pt2InitialMousePos[0], self.pt2LastMousePos[0]) 
				fMouse_Ly = max(self.pt2InitialMousePos[1], self.pt2LastMousePos[1]) 
				fMouse_Rx = max(self.pt2InitialMousePos[0], self.pt2LastMousePos[0]) 
				fMouse_Ry = min(self.pt2InitialMousePos[1], self.pt2LastMousePos[1]) 
				for i in self.listConsideration: 
					#Get the loosebounds of the nodepath 
					sphBounds = i.getModel().getBounds() 
					#Put the center of the sphere into the camera coordinate system 
					#p3 = base.cam.getRelativePoint(render, sphBounds.getCenter()) 
					p3 = base.cam.getRelativePoint(i.getModel().getParent(), sphBounds.getCenter()) 
					#Check if p3 is in the view fustrum 
					p2 = Point2() 
					if base.camLens.project(p3, p2): 
						if (p2[0] >= fMouse_Lx) & (p2[0] <= fMouse_Rx) & (p2[1] >= fMouse_Ry) & (p2[1] <= fMouse_Ly): 
							self.listSelected.append(i) 
							self.funcSelectActionOnObject(i) 
				for i in self.listLastSelected: 
					if not self.kmod.booControl: 
						if i not in self.listSelected: 
							self.funcDeselectActionOnObject(i) 
							pass
					else: 
						self.listSelected.append(i) 
		
		return Task.cont

'''
Possible camera states:
static : not moving and do not react from mouse input
fly	: used to fly throught the world
place  : placing an object (not moving)

note that 'place' status is equivalent to static for camera side
'''

class MyCamera(DirectObject):
	def __init__(self):
		#keyboard/mouse mover
		self.km = KeyboardMover()
		self.mm = MouseMover()
		self.ps = PropSet()
		self.st = SelectionTool()
		#disabling mouse by default
		base.disableMouse()
		#setting status
		self.state = "static"
		
		self.setNearFar(1.0,10000)
		self.setFov(75)
	
	def getKeyboardMover(self):
		return self.km
	
	def getMouseMover(self):
		return self.km
	
	def getSelectionTool(self):
		return self.st
	
	def getFov(self):
		return base.camLens.getFov()
	
	def setNearFar(self,v1,v2):
		base.camLens.setNearFar(v1,v2)
	
	def setFov(self,value):
		base.camLens.setFov(value)

	'''
	This is an interface method used to switch between fly and static 
	modes dinamically through a simple string
	'''
	def getSelected(self):
		return self.st.listSelected
	
	def setState(self,s):
		#if there is a real change in camera state
		if s != self.state:
			#actually change state
			if s == "fly":
				#re-enabling all gui elements
				self.mm.setActive()
				self.km.setActive()
				self.st.setUnactive()
			if s == "static":
				self.mm.setUnactive()
				self.km.setUnactive()
				self.st.setActive()
			#changing state variable at the end of method execution
			self.state = s
	
	def setUtilsActive(self):
		self.accept("tab", self.toggleView)
		self.accept("f", self.ps.toggleFullscreen)
	
	def setUtilsUnactive(self):
		self.ignore("tab")
		self.ignore("f")
	
	def toggleState(self):
		if self.state == "static":
			self.setState("fly")
		else:
			self.setState("static")
	
	def toggleView(self):
		if self.getState() == "fly":
			myGui.showAll()
			myInputHandler.setActive()
		if self.getState() == "static":
			myGui.hideAll()
			myInputHandler.setInactive()
		#switching camera in any case
		self.toggleState()
	
	def getState(self):
		return self.state
