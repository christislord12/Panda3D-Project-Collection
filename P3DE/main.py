from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.task import Task

#world object management
from manager import *
#camera management
from camera import *
#gui
from gui import *
#input management
from inputHandler import InputHandler

#system imports
import sys,__builtin__

#fullscreen e grandezza finestra
loadPrcFileData("","""
fullscreen 0
win-size 800 600
text-encoding utf8
show-frame-rate-meter 1
sync-video 0
""")

class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		#starting all base methods
		__builtin__.myApp = self
		__builtin__.myObjectManager = ObjectManager()
		__builtin__.myGui = MyGui()
		__builtin__.myCamera = MyCamera()
		__builtin__.myInputHandler = InputHandler()
		
		#default config when just opened
		myCamera.mm.showMouse()
		myCamera.setUtilsActive()
		self.defineBaseEvents()
		
		self.mainScene = render.attachNewNode("mainScene")
	
	def getSceneNode(self):
		return self.mainScene
	
	def exportScene(self):
		#hello
		print "DEBUG: executing render ls "
		render.ls()
		

	def defineBaseEvents(self):
		base.accept("escape", sys.exit)

app = MyApp()
app.run()
