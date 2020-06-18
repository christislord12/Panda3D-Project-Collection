
"""
In this example we render each cube with one texture. The prerequisite is, that 
we assign our object at least one texture. If we do not assign a texture here, 
the shader cannot access it later. If you read this Python code first you can 
see that we assign two textures, although on the visual output you can only see 
one texture (remember 0.py). Assigning a texture to a NodePath is like assigning 
a shader input. We need to assign an input, if we have a shader that needs this 
input. But only because there is a setShaderInput, this does not mean we have to 
care about it in the shader.
"""

import sys

import direct.directbase.DirectStart
from pandac.PandaModules import Texture, TextureStage

base.setBackgroundColor(0.0, 0.0, 0.0)
base.disableMouse()

base.camLens.setNearFar(1.0, 50.0)
base.camLens.setFov(45.0)

camera.setPos(0.0, -20.0, 10.0)
camera.lookAt(0.0, 0.0, 0.0)

root = render.attachNewNode("Root")

textureArrow = loader.loadTexture("arrow.png")
textureArrow.setWrapU(Texture.WMClamp)
textureArrow.setWrapV(Texture.WMClamp)

"""
DIRTY
Try to increase the setSort parameter and look at the results. Somehow we can
influence the shader, nevertheless the cube is only textured with one texture.
"""
stageArrow = TextureStage("Arrow")
stageArrow.setSort(1)

textureCircle = loader.loadTexture("circle.png")
textureCircle.setWrapU(Texture.WMClamp)
textureCircle.setWrapV(Texture.WMClamp)

stageCircle = TextureStage("Circle")
stageCircle.setSort(2)

modelCube = loader.loadModel("cube.egg")

cubes = []
for x in [-3.0, 0.0, 3.0]:
    cube = modelCube.copyTo(root)
    cube.setPos(x, 0.0, 0.0)
    cubes += [ cube ]

shader = loader.loadShader("6.sha")
root.setShader(shader)

"""
In this sample we assign all three cubes the same textures. Get another image
and try to assign one cube another texture.
"""
root.setTexture(stageArrow, textureArrow)
root.setTexture(stageCircle, textureCircle)

base.accept("escape", sys.exit)
base.accept("o", base.oobe)

def move(x, y, z):
    root.setX(root.getX() + x)
    root.setY(root.getY() + y)
    root.setZ(root.getZ() + z)

base.accept("d", move, [1.0, 0.0, 0.0])
base.accept("a", move, [-1.0, 0.0, 0.0])
base.accept("w", move, [0.0, 1.0, 0.0])
base.accept("s", move, [0.0, -1.0, 0.0])
base.accept("e", move, [0.0, 0.0, 1.0])
base.accept("q", move, [0.0, 0.0, -1.0])

run()
