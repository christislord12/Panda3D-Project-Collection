
"""
The first useful sample. After this tutorial we are able to draw our cubes,
which look like cubes. With our knowledge we are not able to color them
correctly, but we can do some nice stuff and see the result. If everything is
black this time, something must be wrong.
"""

import sys

import direct.directbase.DirectStart

base.setBackgroundColor(0.0, 0.0, 0.0)
base.disableMouse()

base.camLens.setNearFar(1.0, 50.0)
base.camLens.setFov(45.0)

camera.setPos(0.0, -20.0, 10.0)
camera.lookAt(0.0, 0.0, 0.0)

root = render.attachNewNode("Root")

modelCube = loader.loadModel("cube.egg")

cubes = []
for x in [-3.0, 0.0, 3.0]:
    cube = modelCube.copyTo(root)
    cube.setPos(x, 0.0, 0.0)
    cubes += [ cube ]

shader = loader.loadShader("2.sha")

"""
DIRTY
Try to disable the shader on the root node and then enable it only on one or two
cubes and see what happens. You can do this before you start to modify the
shader.
"""
root.setShader(shader)
#cubes[0].setShader(shader)
#cubes[2].setShader(shader)

"""
DIRTY
If you have tested how you can enable/disable a shader on individual nodes, and
how the scene graph works with shaders, you can modify this lines (comment or
remove the three Python lines above) and load two shaders at the same time. e.g.
2.sha and 1.sha. Apply 2.sha to one cube, and 1.sha to another cube. Because
1.sha does nothing the cube with this shader should disappear.
"""
#shader1 = loader.loadShader("1.sha")
#shader2 = loader.loadShader("2.sha")
#cubes[0].setShader(shader2)
#cubes[1].setShader(shader1)

"""
DIRTY
Do you like to see the model matrix of each cube? You may only understand this
if you read the comment for vshader in 2.sha.
"""
#for cube in cubes:
#    print cube.getMat()

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
