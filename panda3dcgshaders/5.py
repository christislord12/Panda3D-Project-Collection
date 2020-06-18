
"""
In this example we define our own uniforms, we like to send to the GPU.
"""

import sys
import math

from direct.interval.LerpInterval import LerpFunc
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

shader = loader.loadShader("5.sha")
root.setShader(shader)

"""
This is the only new line here. If you comment/remove this line Panda3D sees
that there is a problem. Why? The shader in this example still references to an
uniform, therefore the uniform needs to be set at least once.
"""
root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 1.0)

"""
DIRTY
If you enable to following two lines, without modifying the shader, you have one
more debug utility that may help in some circumstances. With setTransparency
Panda3D instruct the GPU to not only overwrite the color buffer. If the fragment
shader was calculating a color, the GPU reads the old value in the color buffer
back and merges it with the new color. This process is called alpha blending and
most often it is used for transparency. But if transparency is enabled, Panda3D
has to reorder all visible nodes, so they are drawn from back to front (or else
transparency looks not correct). You have to remember this if you "debug" a
scene like this.

Some facts: The new panda3drocks uniform, you can see below, has an alpha
component with a value lesser than 1.0. The background in this scene is black.
Back facing triangles are not drawn. What we conclude from this? If the GPU has
to draw the first cube, the only two colors on the screen are black (0.0, 0.0,
0.0) and a dark purple (0.1, 0.0, 0.1). If the GPU has to draw the second cube,
and they are not side by side, a new purple (theoretically 0.19, 0.0, 0.19,
practically ~0.18, 0.0, ~0.18) appears that is brighter than its predecessor 
(see below for a more detailled explanation). The more triangles are on top of 
one another the brighter the scene. Or in other words, the brighter the scene 
the more the fragment shader needs to be called. Something you should try to 
avoid.
"""
#root.setTransparency(True)
#root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 0.1)

base.accept("escape", sys.exit)
base.accept("o", base.oobe)

def animate(t):
    c = abs(math.cos(math.radians(t)))
    root.setShaderInput("panda3drocks", c, c, c, 1.0)

    """
    DIRTY
    Uncomment only one line at a time and see how the scene graph propagates
    shader inputs.

    As an aside: The setHpr method of a NodePath accepts angles in degrees. But
    Python and Cg internally work with radians (Every FPU known to more than
    0xff people internally works with radians).
    """
    #r = abs(math.cos(math.radians(t + 0.0)))
    #g = abs(math.cos(math.radians(t + 10.0)))
    #b = abs(math.cos(math.radians(t + 20.0)))
    #cubes[0].setShaderInput("panda3drocks", r, 0.0, 0.0, 1.0)
    #cubes[1].setShaderInput("panda3drocks", 0.0, g, 0.0, 1.0)
    #cubes[2].setShaderInput("panda3drocks", 0.0, 0.0, b, 1.0)

interval = LerpFunc(animate, 5.0, 0.0, 360.0)

base.accept("i", interval.start)

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

"""
On more note abount blending. If you enable transparency on a node, Panda3D has
to blend the node together with the existing scene. If you read the Panda3D
manual about this topic, you can see that this is a expensive operation, because
Panda3D has to reorder the scene. So how does this blending work? There is more
than one possibility to blend nodes together. As far as I know Panda3D only uses
the following scheme:

NewDestinationColor = ((1.0 - SourceAlpha) * OldDestinationColor) + (SourceAlpha * SourceColor)

If the there is black screen and we draw the purple triangle with folowing color
attribute 1.0, 0.0, 1.0, 0.1, the following happens:

OldDestinationColor = 0.0, 0.0, 0.0
SourceAlpha = 0.1
SourceColor = 1.0, 0.0, 1.0
=> NewDestinationColor = 0.1, 0.0, 0.1

Our second triangle on top of the first triangle yields:

OldDestinationColor = 0.1, 0.0, 0.1
SourceAlpha = 0.1
SourceColor = 1.0, 0.0, 1.0
=> NewDestinationColor = 0.19, 0.0, 0.19

We assume that the GPU always is calculating with floating point buffers, but
this is not always true. In todays application the color buffer is often not a
floating point buffer, so we see some inaccuracies here. That is the reason why
in the example above I have once written theoretically and then practically.

Why do I explain all this stuff here? Maybe you recognized that this stuff is
once more linear interpolation, but there is no possiblity to influence this
equation with a vertex or fragment shader.
"""