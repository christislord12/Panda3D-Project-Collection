from direct.showbase.ShowBase import ShowBase

import sys, PyCEGUI

# PandaCEGUI import
from eGui.pcegui import PandaCEGUI

class MyApp(ShowBase):
 
	def __init__(self):
		ShowBase.__init__(self)

		# Instantiate CEGUI helper class
		self.CEGUI = PandaCEGUI()

		# Setup CEGUI resources
		self.CEGUI.initializeResources('./eGui/datafiles')

		# Setup our CEGUI layout
		self.setupUI()

		# Enable CEGUI Rendering/Input Handling
		self.CEGUI.enable()
	
	def hideAll(self):
		self.fileManager.setVisible(False)
		self.obProp.setVisble(False)
		
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
		self.CEGUI.System.setDefaultMouseCursor("Vanilla-Images", "MouseArrow")
		self.CEGUI.System.setDefaultFont("DejaVuSans-10")

		root = self.CEGUI.WindowManager.createWindow("DefaultWindow", "MasterRoot")
		self.CEGUI.System.setGUISheet(root)
		
		self.topBar = self.CEGUI.WindowManager.loadWindowLayout("TopBar.layout", "topBar")
		self.fileManager = self.CEGUI.WindowManager.loadWindowLayout("FileManager.layout", "fileManager")
		self.obProp = self.CEGUI.WindowManager.loadWindowLayout("ObjectProperties.layout", "obProp")
		root.addChildWindow(self.topBar)
		root.addChildWindow(self.fileManager)
		root.addChildWindow(self.obProp)
		
		self.topBar.setVisible(True)
		self.fileManager.setVisible(True)
		self.obProp.setVisible(False)
		
		print self.topBar.isVisible()
		
		'''
		# nice button
		self.wnd = self.CEGUI.WindowManager.createWindow("Vanilla/Button", "Demo Window")
		self.wnd.setSize(PyCEGUI.UVector2(PyCEGUI.UDim(0, 100), PyCEGUI.UDim(0, 50)))
		self.wnd.setText("porco dio!")
		root.addChildWindow(self.wnd)
		'''
		

app = MyApp()
app.run() 
