import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import PandaNode,NodePath,Camera,TextNode
from direct.gui.DirectGui import *



def printText(name, message, color):
    text = TextNode(name)
    text.setText(message)
    x,y,z = color
    text.setTextColor(x,y,z, 1)
    text3d = NodePath(text)
    text3d.reparentTo(render)
    return text3d
    

for i in range(0,51):
    printText("X", "|", (1,0,0)).setPos(i,0,0) 

for i in range(0,51):
    printText("Y", "|", (0,1,0)).setPos(0,i,0)  
        
for i in range(0,51):
    printText("Z", "-", (0,0,1)).setPos(0,0,i) 

printText("XL", "X", (0,0,0)).setPos(11.5,0,0) 
printText("YL", "Y", (0,0,0)).setPos(1,10,0) 
printText("YL", "Z", (0,0,0)).setPos(1,0,10) 
printText("OL", "@", (0,0,0)).setPos(0,0,0) 

OnscreenText(text = '(0 , 0)', pos = (.1, .05), scale = 0, fg=(1,1,1,1))
for i in range(-20,20):
    OnscreenText(text = '.', pos = (0, i/float(10)), scale = 0, fg=(1,1,1,1))
for i in range(-20,20):
    OnscreenText(text = '.', pos = (i/float(10), 0), scale = 0, fg=(1,1,1,1))
    
OnscreenText(text = 'X', pos = (1.3, .1), scale = 0, fg=(1,1,1,1))
OnscreenText(text = 'Y', pos = (.1, .9), scale = 0, fg=(1,1,1,1))

OnscreenText(text="Panda 2D/3D: Coordinate System", style=1,  fg=(1,1,1,1), pos=(0.8,-0.95), scale = .07)

OnscreenText(text="Notes:", style=1,  fg=(1,1,1,1), pos=(0.3,0.8), scale = .07)
OnscreenText(text="- Each dot represents 0.10 units", style=1,  fg=(1,1,1,1), pos=(0.64,0.7), scale = .07)
OnscreenText(text="- Each dash represents 1 unit", style=1,  fg=(1,1,1,1), pos=(0.6,0.6), scale = .07)
      
#base.disableMouse()

base.camera.setPos(10,-50,10)

run()


