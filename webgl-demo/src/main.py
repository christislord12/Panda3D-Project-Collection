from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
base = ShowBase()
#m = loader.loadModel('plane.bam')
#m.reparentTo(render)

imageObject = OnscreenImage(image = 'screenshot.jpg',scale = (1.3,1,0.81), pos = (-0, 0, 0.02))
base.setBackgroundColor(0.41,0.41,0.41)
base.run()
