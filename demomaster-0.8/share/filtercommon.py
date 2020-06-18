from pandac.PandaModules import PandaNode, WindowProperties, GraphicsPipe, NodePath
from pandac.PandaModules import FrameBufferProperties, Vec4, RenderState

def makeFilterBuffer(scene, srcbuffer, name, sort, shader, SIZE):
  buffer = base.win.makeTextureBuffer(name, SIZE, SIZE)
  buffer.setSort(sort)
  buffer.setClearColor(Vec4(1, 0, 0, 1))
  bcamera = base.makeCamera2d(buffer)
  bcamera.reparentTo(scene)
  bScene = NodePath("bScene")
  bcamera.node().setScene(bScene)
  card = srcbuffer.getTextureCard()
  card.reparentTo(bScene)
  card.setShader(shader)
  return buffer, bcamera

# These are two functions which help creating two different kind of offscreen buffers.
def createOffscreenBuffer(sort, sizex, sizey):
  winprops = WindowProperties.size(sizex,sizey)
  props = FrameBufferProperties()
  props.setRgbColor(1)
  props.setAlphaBits(1)
  props.setDepthBits(1)
  return base.graphicsEngine.makeOutput(
         base.pipe, "offscreenBuffer",
         sort, props, winprops,
         GraphicsPipe.BFRefuseWindow,
         base.win.getGsg(), base.win)
  # call base.graphicsEngine.removeWindow() to remove this buffer when cleanup

