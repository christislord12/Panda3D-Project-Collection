# -*- coding: utf-8 -*-
"""
Multiple cams example

by: Fabius Astelix
issue: 2009-12-09

"""
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import Point3
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.actor import Actor
import math

import camrack

base.setFrameRateMeter(True)
base.disableMouse()

def changecam(rack):
  info=[
"FPS Cam;sorta FPS cam parented to a moving node, shake the view with an agile device as the pc mouse;press the middle mouse button and roll the view, space for next camera",
"Fixed Tracking Cam;A camera that tracks a moving node from a fixed position;press space for next camera",
"Security Cam;kinda security cam, placed on a fixed position it monotonously rotate its heading from left to right;press space for next camera",
]
  rack.nextcam()
  setinfo(info[rack.activecam])

def setinfo(text):
  title,content,hint=text.split(";")
  infotext['title'].setText(title)
  infotext['content'].setText(content)
  infotext['hint'].setText(hint)

#infotext setup
infotext={}
infotext['title']=OnscreenText(text = 'title', pos = (0, .92), scale = 0.08, mayChange=True, fg=(1,1,1,1), bg=(0,0,1,.7))
infotext['content']=OnscreenText(text = 'content', pos = (0, 0.84), scale = 0.05, mayChange=True, fg=(1,1,0,1), bg=(0,0,0,.5))
infotext['hint']=OnscreenText(text = 'hint', pos = (0, -0.95), scale = 0.07, mayChange=True, fg=(1,1,1,1), bg=(1,0,0,.7))
#
environ = loader.loadModel("models/environment")
environ.reparentTo(render)
environ.setScale(0.25,0.25,0.25)
environ.setPos(-8,42,0)

#Load and move the panda actor
pandaActor = Actor.Actor("models/panda-model",{"walk":"models/panda-walk4"})
pandaActor.setScale(0.005,0.005,0.005)
pandaActor.reparentTo(render)
pandaActor.loop("walk")
if True:
  pandaPosInterval1= pandaActor.posInterval(13,Point3(0,-10,0), startPos=Point3(0,10,0))
  pandaPosInterval2= pandaActor.posInterval(13,Point3(0,10,0), startPos=Point3(0,-10,0))
  pandaHprInterval1= pandaActor.hprInterval(3,Point3(180,0,0), startHpr=Point3(0,0,0))
  pandaHprInterval2= pandaActor.hprInterval(3,Point3(0,0,0), startHpr=Point3(180,0,0))
  #Create and play the sequence that coordinates the intervals
  pandaPace = Sequence(pandaPosInterval1, pandaHprInterval1, pandaPosInterval2, pandaHprInterval2, name = "pandaPace")
  pandaPace.loop()

cams=camrack.camList(
  [
    camrack.camFps(pos=(0,-9,2), hpr=(0,-5,0), parent=pandaActor),
    camrack.camFixedTrk(pos=(0,-50,50), trackto=pandaActor),
    camrack.camSecurity(pos=(0,40,20), hpr=(180,-15,0)),
  ]
)
changecam(cams)
base.accept('space-up', changecam, [cams])

run()
