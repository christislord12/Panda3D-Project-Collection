#!/usr/bin/python

import sys, random
import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *

def clearText():
    directEntry.enterText("")

def displayText(text):
    directEntry.enterText("")
    newTextNode = TextNode('text')
    newTextNode.setText(text)
    newTextNode.setAlign(TextNode.ACenter)
    newTextNode.setWordwrap(16.0)
    text_generate = newTextNode.generate()
    newTextNodePath = render.attachNewNode(text_generate)
    newTextNodePath.setPos(0,20,0)
    textEffects(newTextNodePath)

def textEffects(textNodePath):
    x = random.randint(-5,5)
    y = random.randint(10,40)
    z = random.randint(-5,5)
    tnpPosInterval = LerpPosInterval(textNodePath, 6, Point3(x,y,z))

    r = random.random()
    g = random.random()
    b = random.random()
    a = random.random()
    tnpColorInterval = LerpColorInterval(textNodePath, 6, VBase4(r,g,b,a))

    tnpScaleInterval = LerpScaleInterval(textNodePath, 6, 1+random.random()) 

    current_rotation = textNodePath.getHpr()[2]
    rotation=current_rotation + random.randint(60,120)
    tnpHprInterval = LerpHprInterval(textNodePath, 6, Vec3(0,0,rotation))

    textSequence = Sequence(Parallel(tnpPosInterval,tnpColorInterval,tnpScaleInterval,tnpHprInterval),Func(textEffects, textNodePath))
    textSequence.start()

environ = loader.loadModel("models/environment")
environ.reparentTo(render)
environ.setScale(0.2,0.2,0.2)
environ.setPos(-8,50,-4)

directEntry = DirectEntry(text = "", scale=0.1, width=13, command=displayText,
                          initialText="Type some text then press Enter :)", numLines = 1,
                          focusInCommand=clearText)
directEntry.setPos(Point3(-0.7,0,-0.95))

run()