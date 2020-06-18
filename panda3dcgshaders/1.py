
"""
Our first example with a shader. We only want to show how to load a working
shader. The shader itself is useless, if you activate it, you only see a black
screen. If the shader has an error after all, Panda3D cannot assign it to a
node, obviously, in this case you would see the three cubes. But because we see
nothing, it is an indication that the shader is accepted by the graphic card.
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

"""
Load the shader from a file. But we only load the shader here, nothing would
change if we only add this line.
"""
shader = loader.loadShader("1.sha")

"""
DIRTY
You may disable the shader manually to see that that this Python code has no
flaws. Only the shader is useless, although it has no compile time error.
"""
root.setShader(shader)

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
