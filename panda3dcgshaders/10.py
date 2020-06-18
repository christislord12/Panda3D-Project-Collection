
"""
Nothing new here. It is the same as 9.py.
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

light = render.attachNewNode("Light")
modelLight = loader.loadModel("misc/Pointlight.egg.pz")
modelLight.reparentTo(light)

"""
After reading 10.sha replace cube.egg with cube-smooth.egg once more. Because we
now have per pixel lighting, you see a great visual difference if a light only
covers a small portion of face.
The smaller the faces are, the less you see a difference between per pixel and
per vertex lighting. But if you have large triangles, that may cover your whole
screen, you can see a great difference between this two lighting methods.
"""
modelCube = loader.loadModel("cube.egg")

cubes = []
for x in [-3.0, 0.0, 3.0]:
    cube = modelCube.copyTo(root)
    cube.setPos(x, 0.0, 0.0)
    cubes += [ cube ]

shader = loader.loadShader("10.sha")
for cube in cubes:
    cube.setShader(shader)
    cube.setShaderInput("light", light)

base.accept("escape", sys.exit)
base.accept("o", base.oobe)

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
