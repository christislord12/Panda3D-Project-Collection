from pandac.PandaModules import TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage

class splashCard(object):
  '''this class shows up a splash message'''
  #------------------------------------------------------------
  #
  def __init__(self, image):
    self.myImage=OnscreenImage(image=image, pos = (0, 0, 0),
      parent=base.render2d, scale=(.3,1.,.3)
    )
    self.myImage.setTransparency(TransparencyAttrib.MAlpha)
    #let it shows
    for i in range(4):
      base.graphicsEngine.renderFrame()
  #------------------------------------------------------------
  #
  def destroy(self): self.myImage.destroy()
