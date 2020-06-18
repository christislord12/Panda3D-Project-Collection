# -*- coding: utf-8 -*-
"""
Octree Collisions

by fabius astelix @2010-02-06

Level: INTERMEDIATE

Now we introduce a new term: octree. This is mainly a way to reshape your mesh structure to be more efficient and have higher frame rates in your games. There is a deep David Rose's speech on this subject in the forum that should clear you all that, therefore I'll suggest you to read it here: http://www.panda3d.org/phpbb2/viewtopic.php?p=34405#34405
Here I'll just show you how to prepare your models and scene to use this important technique. Note that this technique will be effective just for collision meshes of an high polygon count - in low count meshes you won't notice appreciable performance improvements.

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you won't find there though, or still isn't clear for you, browse here http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import ActorNode, CollisionHandlerEvent, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay, NodePath
from direct.interval.IntervalGlobal import *

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", """sync-video 0
"""
)
import direct.directbase.DirectStart
#** snippet support routines - not concerning the tutorial part
import snipstuff

#=========================================================================
# Scenographic stuff
#=========================================================================

base.cam.setPos(40, -150, 35)

snipstuff.info.append("Collision Octree")
snipstuff.info.append("A snippet to see performance improvement using octree splitting\nfor collision meshes.")
snipstuff.info.append("Change collision mesh and compare the frame rate difference\n\n1=whole collision mesh\n2=octreefied collision mesh")
snipstuff.info_message("check out the frame rate meter above...")

snipstuff.info_show()

#=========================================================================
# Main
"""
Here we settle up an (apparently) simple scene with a wide terrain surface, where to compare 2 different floor colliders applied on it: the first is a whole single mesh with approx. 16.000 polygons and the other is the same former mesh but after being octreefied, using the octree script incorporated in the blender chicken exporter - have to know that the resulting model is not composed by a whole mesh anymore but rather by dozens of small mesh chunks that will relief the panda collision system for an extent you'll going to see by yourself with this snippet. The real deal with this tutorial is not much how to settle the collisions - explained in detail in former steps - but rather how to export in blender the mesh and how will change here the usual floor collision settings, because of the octree script. Check infos in step10.blend and down here to know what I mean.
"""
#=========================================================================

#** Collision system ignition
base.cTrav=CollisionTraverser()

#** The floor collision handler - all stuff explained in step9
avatarFloorHandler = CollisionHandlerGravity()
avatarFloorHandler.setGravity(9.81+25)
avatarFloorHandler.setMaxVelocity(100)

#** Collision masks
FLOOR_MASK=BitMask32.bit(1)
MASK_OFF=BitMask32.allOff()

#** Our steering avatar
avatarNP=base.render.attachNewNode(ActorNode('smileyNP'))
avatarNP.reparentTo(base.render)
avatar = loader.loadModel('smiley')
avatar.reparentTo(avatarNP)
avatar.setPos(0,0,1)
avatar.setCollideMask(MASK_OFF)
avatarNP.setPos(0,0,15)

#** Stick and set the ray collider to the avatar
raygeometry = CollisionRay(0, 0, 2, 0, 0, -1)
avatarRay = avatarNP.attachNewNode(CollisionNode('avatarRay'))
avatarRay.node().addSolid(raygeometry)
# let's mask our floor FROM collider
avatarRay.node().setFromCollideMask(FLOOR_MASK)
avatarRay.node().setIntoCollideMask(MASK_OFF)

#** This is the terrain map - differently than what we used to in previous steps, the collision solids will be loaded separately. See this below.
terrain = loader.loadModel("oc3ground")
terrain.reparentTo(render)
terrain.setCollideMask(MASK_OFF)
terrain.setScale(10)

#** Let's load ands mask our collision surfaces - I used here a little automation, hope this don't confuse you. By the way, see the warning below because it's the very important thing to know.
floorcolliderdata={
  'normal': {'egg': 'groundc', 'rootname':'normal-root', 'collider': None},
  'oc3fied': {
      'egg': 'groundco3', 'rootname':'octree-root', 'collider': None
  },
}
for data in floorcolliderdata.values():
  m = loader.loadModel(data['egg'])
  m.reparentTo(terrain)
  # WARNING The important thing to know here is that when your collision model mesh will be octreefied, the octree script will change a bit the mesh naming, changing indeed the root name, that we use here to find its geometry and mask it to be recognized by the floor collision handler - in a octreefied mesh the root name will always be (at the date I'm writing and until the script will changes) "octree-root" - just be advised.
  data['collider'] = m.find("**/%s"%data['rootname'])
  data['collider'].node().setIntoCollideMask(MASK_OFF)

#** As usual the floor handler need to know what it got to handle: the ray coupled with the avatar node wrapping everything related to smiley avatar
avatarFloorHandler.addCollider(avatarRay, avatarNP)
base.cTrav.addCollider(avatarRay, avatarFloorHandler)

#** These two functions are here to select from normal to octreefied floor colliders
def oc3_floor_collider():
  floorcolliderdata['oc3fied']['collider'].node().setIntoCollideMask(FLOOR_MASK)
  floorcolliderdata['normal']['collider'].node().setIntoCollideMask(MASK_OFF)
  snipstuff.infotext['message'].setText("Using ocreefied collision mesh")
#
def normal_floor_collider():
  floorcolliderdata['normal']['collider'].node().setIntoCollideMask(FLOOR_MASK)
  floorcolliderdata['oc3fied']['collider'].node().setIntoCollideMask(MASK_OFF)
  snipstuff.infotext['message'].setText("Using single mesh collider")
normal_floor_collider()

snipstuff.DO.accept('1', normal_floor_collider)
snipstuff.DO.accept('2', oc3_floor_collider)

#** Make the smiley roll on the the floor...
def avatarwalk(dt, vel):
  if vel[1]: avatar.setP(avatar.getP()+(20*dt/-vel[1]))
  if vel[0]: avatar.setR(avatar.getR()+(20*dt/vel[0]))
#... and jump
def avatarjump(dt):
  if avatarFloorHandler.isOnGround():
    avatarFloorHandler.addVelocity(20)

#** Now we're ready to activate the avatar steering and go
steering=snipstuff.avatar_steer(avatarNP, avatarwalk, avatarjump, fwspeed=12.)
steering.start()

run()
