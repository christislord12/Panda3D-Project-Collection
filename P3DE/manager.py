from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class WorldObject(DirectObject):
	def __init__(self):
		#setting inner object proprierties
		self.isSelected = False
	
	def setSelected(self,v):
		#setting variable selection
		self.isSelected = v
		
		#callback functions
		if v == True:
			self.selectionEvent()
		else:
			self.deselectionEvent()
	
	def isSelected(self):
		return self.isSelected
	
	#callback of setSelected()
	def selectionEvent(self):
		self.model.showBounds()
	
	#callback of setSelected()
	def deselectionEvent(self):
		self.model.hideBounds()
	
	#reparenting model to mainNode scene
	def setParent(self,node):
		self.model.reparentTo(node)
	
class StaticObject(WorldObject):
	def __init__(self,file = False):
		#calling parent method
		WorldObject.__init__(self)
		
		#private? xD
		self.originalFilename = file
		
		#ppppppppppablic!
		self.locking = False
		
		if file != False:
			self.loadModel(file) #just down here :P
	
	def getFilename(self):
		return self.originalFilename
	
	def getName(self):
		return self.model.getName()
	
	def setName(self,s):
		self.model.setName(s)
	
	def loadPlaceHolder(self,file):
		#hiding real model
		if self.model != False:
			self.model.hide()
		#inserting placeholder
		self.placeholder = loader.loadModel("dataset/"+file)
		self.placeholder.reparentTo(self.model)
	
	def unloadPlaceHolder(self):
		if self.model != False:
			self.model.show()
		self.placeholder.remove()

	def loadModel(self,file):
		#loading model egg file
		self.model = loader.loadModel("dataset/"+file)
		self.model.reparentTo(myApp.getSceneNode())
		#storing type of object in scene
		self.type = "StaticObject"
		#storing options such as lightning
		self.lightning = True
		self.shaders = False
		self.wireframe = False
		self.hidden = False
	
	def getModel(self):
		return self.model
	
	def setLocking(self,v):
		self.locking = v
		#real control is done in InputHandler
	
	def getLocking(self):
		return self.locking
	
	def getWireframe(self):
		isWireframed = self.model.getRenderMode()
		if isWireframed == 0 or isWireframed == 1:
			isWireframed = False
		else:
			isWireframed = True
		return isWireframed
	
	def setLightning(self,v):
		self.lightning = v
		if v == True:
			#setting all lights on
			for l in myObjectManager.lightList:
				self.model.setLight(l.getNodePath())
		else:
			#set all lights off
			self.model.setLightOff()
	
	def getLightning(self):
		return self.lightning
	
	def setShaders(self,v):
		self.shaders = v
		if v == True:
			self.model.setShaderAuto()
		else:
			self.model.setShaderOff()

	def getShaders(self):
		return self.shaders
	
	def setHidden(self,v):
		self.hidden = v
		if v == True:
			pass #needed to be written with a placeholder or something
		else:
			pass #lululul
			
	def getHidden(self):
		return self.hidden

	#warn: not advised to directly set the type
	def setType(self,s):
		self.type = s

	def getType(self):
		return self.type
	
	def remove(self):
		#first remove it from camera
		myCamera.getSelectionTool().removeObject(self)
		#then release memory
		self.model.remove()

class PointLightObject(StaticObject):
	def __init__(self):
		#executing parent class constructor
		StaticObject.__init__(self)
		
		#loading specific model for light
		self.loadModel("models/pointlight.egg")
		self.model.setPos(base.camera,0,10,0)
		self.model.reparentTo(myApp.getSceneNode())
		self.model.setLightOff()
		
		self.plight = PointLight('pointLight')
		self.plight.setColor(VBase4(1, 1, 1, 1))
		self.plnp = self.model.attachNewNode(self.plight)
		render.setLight(self.plnp)
		
		#setting type
		self.setType("PointLightObject")
	
	
	
	def getNodePath(self):
		return self.plnp
	
	def getPandaNode(self):
		return self.plight
	
	#override of virtual method
	def loadModel(self,file):
		#loading model egg file
		self.model = loader.loadModel(file)
	
	def remove(self):
		#deleting light
		render.clearLight(self.plnp)
		self.plnp.remove()
		#first remove it from camera
		myCamera.getSelectionTool().removeObject(self)
		#then release memory
		self.model.remove()

class ObjectManager(DirectObject):
	def __init__(self):
		self.objList = []
		self.lightList = []
		'''self.modifier = ObjectModifier(self)'''
	
	def addPointLight(self):
		p = PointLightObject()
		
		#adding reference to main light list
		self.lightList.append(p)
		#activating model object for light
		myCamera.getSelectionTool().appendObject(p)
		'''
		TODO:
		Sistema tutto il codice in modo che funzioni con la nuova classe PointLightObject
		'''
	
	def addObject(self,filepath):
		obj = StaticObject(filepath)
		#setting space and hierarchy for model
		obj.getModel().setPos(base.camera,0,10,0)
		obj.getModel().wrtReparentTo(myApp.getSceneNode())
		
		#adding object to manager list
		self.objList.append(obj)
		#activating object
		myCamera.getSelectionTool().appendObject(obj)
	
	def removeSelectedObjects(self):
		#avoiding erroneous objects deletion due to
		# oh yeah that's some fukin' nice WASD look at it! wuou! *CLICK*
		# oh dammit you fuckin suckin coder. Fuckin E keypress!
		# :)
		if myCamera.getState() == "fly":
			return
		for obj in myCamera.st.listSelected[:]:
			self.removeObject(obj)
	
	def removeObject(self,obj):
		#removing pointers and switching gui back to basics (tm)
		myGui.noneObjSelected()
		obj.remove()
		if obj.getType() == "StaticObject":
			self.objList.remove(obj)
		elif obj.getType() == "PointLightObject":
			self.lightList.remove(obj)
	
	def getObjectList(self):
		return self.objList
	
