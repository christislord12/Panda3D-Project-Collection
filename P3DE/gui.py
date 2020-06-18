from direct.task import Task
from direct.showbase.DirectObject import DirectObject

import sys, os, string, PyCEGUI

# PandaCEGUI import
from eGui.pcegui import PandaCEGUI



class MyGui(DirectObject):
 
	def __init__(self):
		# Instantiate CEGUI helper class
		self.CEGUI = PandaCEGUI()

		# Setup CEGUI resources
		self.CEGUI.initializeResources('./eGui/datafiles')

		# Setup our CEGUI layout
		self.setupUI()

		# Enable CEGUI Rendering/Input Handling
		self.CEGUI.enable()
		
		# Populating Listbox with files
		#setting current working directory
		self.populateListbox()
		
		# Setting up customs events
		self.setupEvents()
		
	
	def hideAll(self):
		self.fileManager.setVisible(False)
		self.obProp.setVisible(False)
		
	def showAll(self):
		self.fileManager.setVisible(True)
		#self.obProp.setVisible(True)
	
	def togglePanel(self):
		if self.fileManager.isVisible():
			self.fileManager.setVisible(False)
			self.obProp.setVisible(True)
		else:
			self.fileManager.setVisible(True)
			self.obProp.setVisible(False)

	def setupUI(self):
		self.CEGUI.SchemeManager.create("TaharezLook.scheme")
		self.CEGUI.SchemeManager.create("VanillaSkin.scheme")
		self.CEGUI.System.setDefaultFont("DejaVuSans-10")

		self.root = self.CEGUI.WindowManager.createWindow("DefaultWindow", "MasterRoot")
		self.root.setProperty("UnifiedPosition","{{0.0,0},{0.0,0}}")
		self.root.setProperty("UnifiedSize","{{1.0,0},{1.0,0}}")
		self.CEGUI.System.setGUISheet(self.root)
		
		self.topBar = self.CEGUI.WindowManager.loadWindowLayout("TopBar.layout")
		self.fileManager = self.CEGUI.WindowManager.loadWindowLayout("FileManager.layout")
		self.obProp = self.CEGUI.WindowManager.loadWindowLayout("ObjectProperties.layout")
		self.pointLightProp = self.CEGUI.WindowManager.loadWindowLayout("LightProperties.layout")
		self.root.addChildWindow(self.topBar)
		self.root.addChildWindow(self.fileManager)
		self.root.addChildWindow(self.obProp)
		self.root.addChildWindow(self.pointLightProp)
		
		self.pointLightProp.setVisible(False)
		self.topBar.setVisible(True)
		self.fileManager.setVisible(True)
		self.obProp.setVisible(False)
		
		self.listBox = self.fileManager.getChildRecursive("FileManager/Listbox")
	
	def populateListbox(self, filter = False):
		self.currentPath = os.getcwd()+"\dataset"
		self.itemList = []
		self.fileList = []
		self.itemsTextColours = PyCEGUI.ColourRect(PyCEGUI.colour(0,0,0,1))
		self.itemsSelectColours = PyCEGUI.ColourRect(PyCEGUI.colour(1,1,1,0.3))
		
		#adding ListboxTextItem to cegui Listbox
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
				item = PyCEGUI.ListboxTextItem(file)
				item.setTextColours(self.itemsTextColours)
				item.setSelectionColours(self.itemsSelectColours)
				item.setSelectionBrushImage("TaharezLook", "ListboxSelectionBrush")
				item.setAutoDeleted(False)
				self.fileList.append(file)
				self.itemList.append(item)
				self.listBox.addItem(item)
		
	
	def eventListbox(self, task):
		for item in self.itemList:
			if item.isSelected() == True:
				#adding object to scene (only once per selection)
				filename = item.getText()
				myObjectManager.addObject(filename)
				item.setSelected(False)
		return Task.cont
	
	def selectionChanged(self, e):
		item = self.fileManager.getChildRecursive("FileManager/Listbox").getFirstSelectedItem()
		myObjectManager.addObject(item.getText())
	
	def searchInList(self,e):
		search = self.fileManager.getChildRecursive("FileManager/Editbox").getText()
		
		#clearing list
		self.listBox.resetList()
		for item in self.itemList[:]:
			self.itemList.remove(item)
		
		if len(search)==0:
			for file in self.fileList:
				item = PyCEGUI.ListboxTextItem(file)
				item.setTextColours(self.itemsTextColours)
				item.setSelectionColours(self.itemsSelectColours)
				item.setSelectionBrushImage("TaharezLook", "ListboxSelectionBrush")
				item.setAutoDeleted(False)
				self.itemList.append(item)
				self.listBox.addItem(item)
		else:
			for file in self.fileList:
				if not file.find(search):
					item = PyCEGUI.ListboxTextItem(file)
					item.setTextColours(self.itemsTextColours)
					item.setSelectionColours(self.itemsSelectColours)
					item.setSelectionBrushImage("TaharezLook", "ListboxSelectionBrush")
					item.setAutoDeleted(False)
					self.itemList.append(item)
					self.listBox.addItem(item)
			
	def hideAll(self):
		self.pointLightProp.setVisible(False)
		self.fileManager.setVisible(False)
		self.obProp.setVisible(False)
	
	def manyObjSelected(self):
		print "hehehehe speravi che l'avessi implementato neeeh? :)"
		#remove me after writing
		self.noneObjSelected()
	
	def oneObjSelected(self):
		obj = myCamera.getSelected()[0]
		
		#if type is a point light
		if obj.getType() == "PointLightObject":
			print "INFO: loading pointLight specific gui panel"
			self.hideAll()
			self.pointLightProp.setVisible(True)
			
			#setting name
			name = obj.getName()
			self.pointLightProp.getChildRecursive("LightProperties/NPNameEditbox").setProperty("Text", name)
			
			#setting locking
			isLocked = obj.getLocking()
			self.pointLightProp.getChildRecursive("LightProperties/LockCheckbox").setSelected(isLocked)
		
		if obj.getType() == "StaticObject":
			#if object type is a static object load static object specific panel gui
			self.hideAll()
			self.obProp.setVisible(True)
			# LOADING fukka stuff
			# getting first element of list returned by camera object selection instance
			# which is what I need
			obj = myCamera.getSelected()[0]
			
			#setting name
			name = obj.getName()
			self.obProp.getChildRecursive("ObjectProperties/NPNameEditbox").setProperty("Text", name)
			
			#setting locking
			isLocked = obj.getLocking()
			self.obProp.getChildRecursive("ObjectProperties/LockCheckbox").setSelected(isLocked)
			
			#setting lighting
			isLightened = obj.getLightning()
			self.obProp.getChildRecursive("ObjectProperties/LightingCheckbox").setSelected(isLightened)
			
			#setting shaders
			isShaded = obj.getShaders()
			self.obProp.getChildRecursive("ObjectProperties/ShaderCheckbox").setSelected(isShaded)
			
			#setting wireframe
			isWireframed = obj.getWireframe()
			self.obProp.getChildRecursive("ObjectProperties/WireframeCheckbox").setSelected(isWireframed)
	
	def noneObjSelected(self):
		self.hideAll()
		self.fileManager.setVisible(True)
	
	def ping(self):
		print "myGui ping!"
	
	# Function has e because triggered as an event from CEGUI
	def focusOnSearchBox(self,e):
		myInputHandler.setInactive()
		myCamera.setUtilsUnactive()
		self.fileManager.getChildRecursive("FileManager/Editbox").activate()
	
	# Function has e because triggered as an event from CEGUI
	def focusNotOnSearchBox(self,e):
		myInputHandler.setActive()
		myCamera.setUtilsActive()
		self.fileManager.getChildRecursive("FileManager/Editbox").deactivate()
	
	def focusOnNPName(self,e):
		myInputHandler.setInactive()
		myCamera.setUtilsUnactive()
		self.obProp.getChildRecursive("ObjectProperties/NPNameEditbox").activate()
	
	def focusNotOnNPName(self,e):
		self.changeObjName()
		
		myInputHandler.setActive()
		myCamera.setUtilsActive()
		self.obProp.getChildRecursive("ObjectProperties/NPNameEditbox").deactivate()
	
	def focusOnPLNPName(self,e):
		myInputHandler.setInactive()
		myCamera.setUtilsUnactive()
		self.pointLightProp.getChildRecursive("LightProperties/NPNameEditbox").activate()
	
	def focusNotOnPLNPName(self,e):
		self.changePLObjName()
		
		myInputHandler.setActive()
		myCamera.setUtilsActive()
		self.pointLightProp.getChildRecursive("LightProperties/NPNameEditbox").deactivate()
	
	def changeObjName(self):
		obj = myCamera.getSelected()[0]
		newName = self.obProp.getChildRecursive("ObjectProperties/NPNameEditbox").getProperty("Text")
		
		obj.setName(newName)
	
	def changePLObjName(self):
		obj = myCamera.getSelected()[0]
		newName = self.pointLightProp.getChildRecursive("LightProperties/NPNameEditbox").getProperty("Text")
		
		obj.setName(newName)
	
	def changedLighting(self,e):
		obj = myCamera.getSelected()[0]
		checkbox = self.obProp.getChildRecursive("ObjectProperties/LightingCheckbox")
		#setting light as checkbox value
		obj.setLightning(checkbox.isSelected())
	
	def changedWireframe(self,e):
		obj = myCamera.getSelected()[0]
		checkbox = self.obProp.getChildRecursive("ObjectProperties/WireframeCheckbox")
		if checkbox.isSelected():
			obj.getModel().setRenderModeWireframe() 
		else:
			obj.getModel().setRenderModeFilled() 
	
	def changedHidden(self,e):
		obj = myCamera.getSelected()[0]
		
		checkbox = self.obProp.getChildRecursive("ObjectProperties/HiddenCheckbox")
		obj.setHidden(checkbox.isSelected())
	
	def changedShader(self,e):
		obj = myCamera.getSelected()[0]
		
		checkbox = self.obProp.getChildRecursive("ObjectProperties/ShaderCheckbox")
		obj.setShaders(checkbox.isSelected())
		
	def changedLock(self,e):
		obj = myCamera.getSelected()[0]
		checkbox = self.obProp.getChildRecursive("ObjectProperties/LockCheckbox")
		obj.setLocking(checkbox.isSelected())
	
	def changedPointLightLock(self,e):
		#indipendent from type
		obj = myCamera.getSelected()[0]
		checkbox = self.pointLightProp.getChildRecursive("LightProperties/LockCheckbox")
		obj.setLocking(checkbox.isSelected())
	
	def setupEvents(self):
		#file manager events management
		self.fileManager.getChildRecursive("FileManager/Editbox").subscribeEvent(PyCEGUI.Window.EventMouseEnters, self, "focusOnSearchBox")
		self.fileManager.getChildRecursive("FileManager/Editbox").subscribeEvent(PyCEGUI.Window.EventMouseLeaves, self, "focusNotOnSearchBox")
		self.fileManager.getChildRecursive("FileManager/Editbox").subscribeEvent(PyCEGUI.Editbox.EventTextAccepted, self, "searchInList")
		self.fileManager.getChildRecursive("FileManager/Listbox").subscribeEvent(PyCEGUI.Listbox.EventSelectionChanged, self, "selectionChanged")
		
		#object properties events management
		self.obProp.getChildRecursive("ObjectProperties/NPNameEditbox").subscribeEvent(PyCEGUI.Window.EventMouseEnters, self, "focusOnNPName")
		self.obProp.getChildRecursive("ObjectProperties/NPNameEditbox").subscribeEvent(PyCEGUI.Window.EventMouseLeaves, self, "focusNotOnNPName")
		
		self.pointLightProp.getChildRecursive("LightProperties/NPNameEditbox").subscribeEvent(PyCEGUI.Window.EventMouseEnters, self, "focusOnPLNPName")
		self.pointLightProp.getChildRecursive("LightProperties/NPNameEditbox").subscribeEvent(PyCEGUI.Window.EventMouseLeaves, self, "focusNotOnPLNPName")
		
		self.obProp.getChildRecursive("ObjectProperties/LightingCheckbox").subscribeEvent(PyCEGUI.Checkbox.EventCheckStateChanged, self, "changedLighting")
		
		self.obProp.getChildRecursive("ObjectProperties/LockCheckbox").subscribeEvent(PyCEGUI.Checkbox.EventCheckStateChanged, self, "changedLock")
		self.pointLightProp.getChildRecursive("LightProperties/LockCheckbox").subscribeEvent(PyCEGUI.Checkbox.EventCheckStateChanged, self, "changedPointLightLock")
		
		self.obProp.getChildRecursive("ObjectProperties/ShaderCheckbox").subscribeEvent(PyCEGUI.Checkbox.EventCheckStateChanged, self, "changedShader")
		
		self.obProp.getChildRecursive("ObjectProperties/WireframeCheckbox").subscribeEvent(PyCEGUI.Checkbox.EventCheckStateChanged, self, "changedWireframe")
		
		self.obProp.getChildRecursive("ObjectProperties/HiddenCheckbox").subscribeEvent(PyCEGUI.Checkbox.EventCheckStateChanged, self, "changedHidden")
		
