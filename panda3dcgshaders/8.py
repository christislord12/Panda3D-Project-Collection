"""
Like 0.py we restart from scratch and create a basic example with one point
light, that only supports diffuse lighting. There is no shader attached to this
example. If you do not understand this sample then open the Panda3D manual and
try to understand e.g. the Disco-Lights sample.

When we talk about lighting we talk about an "effect" that we can see with our
eyes. Live is a game, just with better graphic. Lighting is still something you
may do your own research and invent a cool new idea, no one had before. We often
only approximate lighting and invent new terms that do not exist in reality e.g.
there is no specular light in real live. For better lighting we often need to
pre calculate some values in an often slow pre process. We start here only with
one basic lighting model: Diffuse Lighting.

The basic idea of diffuse lighting is: The steeper the angle between the light
and a surface, the less light particles can reach the surface. The following
figures show an example with a directional light and a wall.

1. 100% of the light reaches the wall.
2. ~50% of the light reaches the wall.
3. 0% of the light reaches the wall.

      |           /
1. -> |    2. -> /     3. -> ---
      |         /

If no light reaches a wall, the wall cannot reflect any light particles and
therefore you cannot see anything. This idea is only one basic idea. This idea
e.g. says nothing about the fact that if a wall reflects some light, it may be
possible that this light reaches another wall, which may reflect this light
particles once more.

Given that there is one wall behind another wall:

   |    |
-> |    |
   |    |

If we translate our idea to this situation, it means, that both walls got the
same amount of light, because the angle between the light surface and the light
source is equal for both walls. This is of course dead wrong, because the first
wall occludes the second wall, so there is more or less no light at all.

The default lighting model the fixed function pipeline offers to Panda3D has
tons of flaws, even though it helps to increase realism. Let us stick to this
mediocre lighting model for now (better lighting models are often extremely slow
and only with tricks you may use them in 60 FPS applications).

To calculate how much light reaches our triangle (or wall) we need a tool that
helps us to distinguish if a triangle looks toward a light source or not. One
possibility to do this is a surface normal. In the preceding examples we assumed
that the surface normal is perpendicular to the surface. This is not always
true, as we see later, therefore we like to define a normal at least for each
triangle (or face). When you have a look at the cube.egg once more you see that
for every polygon, a normal is specified. If Panda3D needs to triangulate the
model for the GPU it assigns every triangle, that belongs to the same polygon,
the same normal.

That is not the whole truth, in fact, the GPU likes to have a normal for every
vertex. Why this is a good idea, is shown by another example. Open the enclosed
figures.svg or figures.png and look at figure 8-1. If we have a cube, there are
at least two possibilities to assign normals. The visual difference you may see
later is that the left cube has sharp edges, while the right cube has smooth
edges (on the right cube, the normals on each corner have a small gap in
between, this gap is only here to see that every vertex has a normal). Metal
like objects may have sharper edges while wooden objects may not. An artist may
influence how a model looks like (with lighting enabled) if he/she modifies the
normals. Back to our "whole truth" problem. As you can see it is impossible to
create a smooth cube if every polygon or triangle only has one normal. We need
at least one normal for every vertex.

The cube.egg model is an example of cube with sharp edges, while the
cube-smooth.egg model is an example of a cube with smooth edges. Try to see the
difference between this two files.

The fixed function pipeline of a GPU (that is the pipeline Panda3D uses if there
is no call to setShader or setAutoShader) is not that sophisticated. Better said
the GPUs were not powerful enough to calculate this very simple lighting model
per fragment/pixel, they only can calculate it per vertex. The larger your
triangles on your screen, the falser the result.

One more definition for diffuse lighting is, that it does not depend on the
viewers position. That is not true for all effects e.g. the "output" of a mirror
depends on the viewers position. Specular lighting simulates a mirror like
effect for lights and therefore depends on the viewers position.

Diffuse lighting is especially suited for rough surfaces, because of our
definition that the surfaces should distribute light in any direction,
independent of any other environmental effects.

Back to our problem: We have a surface normal, we have a light position and we
say that only this two things should matter. We now can calculate a direction
vector from the light to our triangle. Because it is a point light, that
distributes light in any direction, this assumption is correct. After this first
operation we calculate the angle between this direction and surface normal.
Based on this angle we can calculate how much diffuse light we have on a
triangle.

        |          |
1. -> <-|    2. -> |->
        |          |

In example 1. we have 100% diffuse light while in the example 2. there is 0%
diffuse lighting.

There are two possibilities to calculate this angle. We do some trigonometry, or
we use the dot product. Both ideas are equivalent, but the second is faster to
calculate.

Read the following page to get in-depth information.

http://en.wikipedia.org/wiki/Dot_product

We will later see how to calculate exactly each of this steps. I only like to
introduce some concepts here.
"""

import sys
import math

import direct.directbase.DirectStart
from direct.interval.LerpInterval import LerpFunc
from pandac.PandaModules import PointLight

base.setBackgroundColor(0.0, 0.0, 0.0)
base.disableMouse()

base.camLens.setNearFar(1.0, 50.0)
base.camLens.setFov(45.0)

camera.setPos(0.0, -20.0, 10.0)
camera.lookAt(0.0, 0.0, 0.0)

root = render.attachNewNode("Root")

"""
We set up a default point light here. You may modify the color of the light, but
in the next examples we assume, that the light has no attenuation and is white.

There is a dummy model attached to this node, to see where the light should be.
Because this light is parented to render, and we only enable light on the cubes,
this model does not influence the lighting nor is it lit by the light itself.
"""
pointlight = PointLight("Light")
light = render.attachNewNode(pointlight)
modelLight = loader.loadModel("misc/Pointlight.egg.pz")
modelLight.reparentTo(light)

"""
DIRTY
Replace cube.egg with cube-smooth.egg and try to understand why both outputs
differ.
"""
modelCube = loader.loadModel("cube.egg")

cubes = []
for x in [-3.0, 0.0, 3.0]:
    cube = modelCube.copyTo(root)
    cube.setPos(x, 0.0, 0.0)
    cube.setLight(light)
    cubes += [ cube ]

base.accept("escape", sys.exit)
base.accept("o", base.oobe)

"""
We move around our light. Because this basic application only supports per
vertex lighting you often can see some odd artifacts if only one vertex of a
face is lit.

The bounding box around all cubes ranges from (-4.0, -1.0, -1.0) to (4.0, 1.0,
1.0). Therefore we set the radius of the virtual sphere (the motion path of the
light) to something that is only a little bit larger than 4.0. This helps later
to see the visual difference from per vertex lighting to per pixel lighting.
"""
def animate(t):
    radius = 4.3
    angle = math.radians(t)
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    z = math.sin(angle) * radius
    light.setPos(x, y, z)

def intervalStartPauseResume(i):
    if i.isStopped():
        i.start()
    elif i.isPaused():
        i.resume()
    else:
        i.pause()

interval = LerpFunc(animate, 10.0, 0.0, 360.0)

base.accept("i", intervalStartPauseResume, [interval])

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
