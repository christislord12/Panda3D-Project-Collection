
"""
In this example we start to pass our own variables from the vertex shader to the
fragment shader.
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

shader = loader.loadShader("4.sha")
root.setShader(shader)

"""
DIRTY
Uncomment this line only after you read the comment in the shader.

Each one of the three cubes has a different position. Before Panda3D sends the
vertices to the graphic card it sends a matrix to the GPU that instructs the GPU
to move all vertices to the new position (only if there is no shader, with a
shader we have to do this on our, as you already know). The advantage is that
Panda3D can send the exact same vertices to the GPU for all three cubes. After
calling flattenLight we have a different situation. Panda3D applies this move
command on itself to the vertices. Prior to this modification every cube need
his own set of vertices, because they cannot share their vertices anymore. The
output of the call to render.analyze may help to see what happens. Advantage in
this case is that Panda3D does not have to send the GPU a command to move the
object around. But the vertices now have new values, so the output of shader may
change too. Try to understand why the cubes[0].getX() does not display the same
value before and after the call to flattenLight.

You only can see a visible change if the vertex shader contains the following
command (the color should depend on the position):

l_my = vtx_position * 0.5 + 0.5;

Try to understand where and why the output differs.
"""
#render.analyze()
#print cubes[0].getX()
#root.flattenLight()
#render.analyze()
#print cubes[0].getX()

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
