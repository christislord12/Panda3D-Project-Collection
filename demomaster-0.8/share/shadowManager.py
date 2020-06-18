""" shadowManager.py
The program is modified from pro-rsoft's post.
==>
Author:       pro-rsoft (niertie1@gmail.com)
Description:  Contains the ShadowManager class, which manages shadows for
              a scene, and supports both soft and hard shadows.
License:      zlib/libpng license:

Copyright (c) 2008 pro-rsoft

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

    1. The origin of this software must not be misrepresented; you must not
    claim that you wrote the original software. If you use this software
    in a product, an acknowledgment in the product documentation would be
    appreciated but is not required.

    2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.

    3. This notice may not be removed or altered from any source
    distribution.
"""
__all__ = ["ShadowManager"]

from pandac.PandaModules import GraphicsOutput, Texture, NodePath, Vec3, Point3
from pandac.PandaModules import PandaNode, WindowProperties, GraphicsPipe
from pandac.PandaModules import FrameBufferProperties, Vec4, RenderState

import demobase
from filtercommon import *


class ShadowManager(demobase.Att_base):
  """This class manages shadows for a scene."""

  def __init__(self, scene = base.render, ambient = 0.2, hardness = 16, fov = 40, near = 10, far = 200, blur=True, SIZE=512):
    """Create an instance of this class to initiate shadows.
    Also, a shadow casting 'light' is created when this class is called.
    The first parameter is the nodepath in the scene where you
    want to apply your shadows on, by default this is render."""
    demobase.Att_base.__init__(self, False, "Shadow Manager")

    # Read and store the function parameters
    self.scene = scene
    self.__ambient = ambient
    self.__hardness = hardness
    self.blur = blur

    # By default, mark every object as textured.
    self.flagTexturedObject(self.scene)

    # Create the buffer plus a texture to store the output in
    self.buffer = createOffscreenBuffer(-3,SIZE,SIZE)
    self.depthmap = Texture()
    self.buffer.addRenderTexture(self.depthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

    # Set the shadow filter if it is supported
    if(base.win.getGsg().getSupportsShadowFilter()):
      self.depthmap.setMinfilter(Texture.FTShadow)
      self.depthmap.setMagfilter(Texture.FTShadow)

    # Make the camera
    #lightnode = scene.attachNewNode("lightcam")
    self.light = base.makeCamera(self.buffer)
    self.light.reparentTo(scene)
    self.light.node().setScene(self.scene)
    self.light.node().getLens().setFov(fov)
    self.light.node().getLens().setNearFar(near, far)
    self._lookat = (0,0,0)

    # Put a shader on the Light camera.
    lci = NodePath(PandaNode("lightCameraInitializer"))
    lci.setShader(loader.loadShader("shaders/caster.sha"))
    self.light.node().setInitialState(lci.getState())

    # Put a shader on the Main camera.
    mci = NodePath(PandaNode("mainCameraInitializer"))
    mci.setShader(loader.loadShader("shaders/softshadow.sha"))
    #self.savestate = base.cam.node().getInitialState()
    base.cam.node().setInitialState(mci.getState())

    # Set up the blurring buffers, one that blurs horizontally, the other vertically
    if self.blur:
        self.blurXBuffer = makeFilterBuffer(scene, self.buffer, "Blur X", -2, loader.loadShader("shaders/blurx.sha"), SIZE)
        self.blurYBuffer = makeFilterBuffer(scene, self.blurXBuffer[0], "Blur Y", -1, loader.loadShader("shaders/blury.sha"), SIZE)
        self.scene.setShaderInput("depthmap", self.blurYBuffer[0].getTexture())
    else:
        self.scene.setShaderInput("depthmap", self.buffer.getTexture())

    # Set the shader inputs
    self.scene.setShaderInput("light", self.light)
    self.scene.setShaderInput("props", ambient, hardness, 0, 1)

  def Destroy(self):
      # clear shaders on camera
      #base.cam.node().setInitialState(self.savestate)
      base.cam.node().setInitialState(RenderState.makeEmpty())
      #base.cam.node().setInitialState(render.getState())
      base.cam.reparentTo(base.camera)

      self.light.node().setInitialState(RenderState.makeEmpty())
      self.light.removeNode()
      base.graphicsEngine.removeWindow(self.buffer)

      if self.blur:
          self.blurXBuffer[1].removeNode()
          self.blurYBuffer[1].removeNode()
          base.graphicsEngine.removeWindow(self.blurXBuffer[0])
          base.graphicsEngine.removeWindow(self.blurYBuffer[0])



  def flagUntexturedObject(self, object):
    """Marks the supplied object as untextured. The shader needs to know this for
    every untextured object, because otherwise the shader will make it all black."""
    object.setShaderInput("texDisable", 1, 1, 1, 1)

  def flagTexturedObject(self, object):
    """Marks the supplied object as textured. By default, all objects are already
    marked as textured, but if you manually flag an object as untextured, you can use
    this function to revert."""
    object.setShaderInput("texDisable", 0, 0, 0, 0)

  def setAmbient(self, ambient):
    """Returns the ambient of the scene. This is a value between 0 and 1.
    0 is very dark, while 1 is very light. Usually a value like 0.2 is recommended."""
    self.__ambient = ambient
    self.scene.setShaderInput("props", self.__ambient, self.__hardness, 0, 1)

  def getAmbient(self):
    """Returns the ambient of the scene. This is a value between 0 and 1.
    0 is very dark, while 1 is very light. Usually a value like 0.2 is recommended."""
    return self.__ambient

  def setHardness(self, hardness):
    """Sets the hardness of the shadows. This is usually a value higher than 0.
    64 is usually a good value for very hard shadows, while at a value of 0,
    the shadows are so soft they are unnoticable. Usually a value near 16 is recommended,
    but this may vary on the scene and you may need to experiment a bit with this value."""
    self.__hardness = hardness
    self.scene.setShaderInput("props", self.__ambient, self.__hardness, 0, 1)

  def getHardness(self, hardness):
    """Returns the hardness of the shadows. This is usually a value higher than 0.
    64 is usually a good value for very hard shadows, while at a value of 0,
    the shadows are so soft they are unnoticable. Usually a value near 15 is recommended,
    but this may vary on the scene and you may need to experiment a bit with this value."""
    return self.__hardness

  def getLight(self):
    """Returns a NodePath which represents the light and shadow caster.
    You can also directly access the light using ShadowManager.light."""
    return self.light

  def setFov(self,fov):
    """Sets the field-of-view, in degrees, of the light."""
    self.light.node().getLens().setFov(fov)

  def getFov(self):
    """Returns the field-of-view, in degrees, of the light."""
    return self.light.node().getLens().getFov()

  def setFar(self, far):
    """Sets the far distance of the light."""
    self.light.node().getLens().setFar(far)

  def getFar(self):
    """Returns the far distance of the light."""
    return self.light.node().getLens().getFar()

  def setNear(self, near):
    """Sets the near distance of the light."""
    self.light.node().getLens().setNear(near)

  def getNear(self):
    """Returns the near distance of the light."""
    return self.light.node().getLens().getNear()

  def setNearFar(self, near, far):
    """Shorthand function to set both the near and far clip of the camera."""
    self.light.node().getLens().setNearFar(near, far)

  def setStandardControl(self):
        self.att_ambient = demobase.Att_FloatRange(False, "Ambient", 0.0, 1.0, self.__ambient)
        self.att_ambient.setNotifier(self.changeParams)
        self.att_hardness = demobase.Att_IntRange(False, "Hardness", 0, 100, self.__hardness)
        self.att_hardness.setNotifier(self.changeParams)
        fov = self.light.node().getLens().getFov()
        self.att_fov = demobase.Att_FloatRange(False, "Fov", 10.0, 200.0, fov[0], 0)
        self.att_fov.setNotifier(self.changeParams)
        near  = self.light.node().getLens().getNear()
        far = self.light.node().getLens().getFar()
        self.att_near = demobase.Att_FloatRange(False, "Near", 5.0, 200.0, near, 0)
        self.att_near.setNotifier(self.changeParams)
        self.att_far = demobase.Att_FloatRange(False, "Far", 5.0, 200.0, far, 0)
        self.att_far.setNotifier(self.changeParams)
        pos = self.light.getPos()
        self.att_lightpos = demobase.Att_Vecs(False, "Light Pos", 3, pos, -200, 200)
        self.att_lightpos.setNotifier(self.changeLight)
        self.att_lightat = demobase.Att_Vecs(False, "LookAt", 3, self._lookat, -30, 30)
        self.att_lightat.setNotifier(self.changeLight)

  def changeParams(self, object):
        self.setAmbient(self.att_ambient.v)     # Most of these five are the default
        self.setHardness(self.att_hardness.v)   # values so it was kinda unnecessary to
        self.setFov(self.att_fov.v)            # set them explicitly but I wanted to
        if self.att_near.v < self.att_far.v:
            self.setNearFar(self.att_near.v, self.att_far.v)               # show how to set them anyway.

  def changeLight(self, object):
        pos = self.att_lightpos.getValue()
        #self.light.setPos(v[0],v[1],v[2])
        #self.light.lookAt(0,0,self.roomheight/4)
        lookat = self.att_lightat.getValue()
        #self.light.lookAt(v[0],v[1],v[2])
        self.changeLightPos(Vec3(pos[0],pos[1],pos[2]), Point3(lookat[0],lookat[1],lookat[2]))


  def changeLightPos(self, pos, lookat):
      if pos != None:
        self.light.setPos(pos)
      if lookat != None:
        self.light.lookAt(lookat)
        self._lookat = (lookat[0],lookat[1],lookat[2])
