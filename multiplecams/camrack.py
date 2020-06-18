# -*- coding: utf-8 -*-
"""
Multiple cams management using the just the base.camera node

"""
from pandac.PandaModules import Point3
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Camera
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.actor import Actor
import math

#just in case isn't already disabled
base.disableMouse()

#========================================================================
#
class camList(object):
  def __init__(self, cams=[], startingcam=0):
    self.cams=cams
    self.activecam=None
    self.changecam(startingcam)

  def nextcam(self):
    if len(self.cams):
      nextcam=self.activecam+1 if self.activecam < (len(self.cams)-1) else 0
      self.changecam(nextcam)

  def changecam(self, index):
    if len(self.cams):
      if (index <> self.activecam):
        if self.activecam <> None:
          self.cams[self.activecam].setActive(False)
        self.activecam=index
        self.cams[self.activecam].setActive(True)

#========================================================================
#
class camRack(object):
  """ ancestor
  """
  def __init__(self, **keys):
    self._parent=keys.get('parent', base.render)
    self._pos=keys.get('pos', (0,0,0))
    self._hpr=keys.get('hpr', None)
    self._polltime=keys.get('polltime', 1.0)
    #to manage update task - note that to have it working the child must have an update method defined
    self._updatetask=None

  #----------------------------------------------------
  #
  def setActive(self, on=True):
    """ if a derived class got an update method, it will automatically be activated/deactivated an update task polling
    """
    if on:
      base.camera.reparentTo(self._parent)
      # rescale the cam position according with the parent scale
      scale=self._parent.getScale()
      self.setPos(Point3(*map(lambda a,b: a/b, self._pos, scale)))
      if not self._hpr:
        base.camera.lookAt(0,0,0)
        self._hpr=base.camera.getHpr()
      self.setHpr(self._hpr)

      if hasattr(self, 'update'):
        self._updatetask=taskMgr.doMethodLater(
          self._polltime, self.update, "crUpdCamera"
        )
    else:
      if hasattr(self, 'update') and self._updatetask:
        taskMgr.remove("crUpdCamera")
        self._updatetask=None

  #----------------------------------------------------
  #
  def setPos(self, pos):
    base.camera.setPos(pos)

  #----------------------------------------------------
  #
  def setHpr(self, hpr):
    base.camera.setHpr(hpr)

#========================================================================
#
class camFixedTrk(camRack):
  """ A fixed position camera that tracks a fixed or moving node
  """
  def __init__(self, trackto=None, rotspeed=1.0, **keys):
    camRack.__init__(self, **keys)
    self.tracker=Tracker(parent=base.camera, rotspeed=rotspeed)
    if trackto: self.trackTo(trackto)

  #----------------------------------------------------
  #
  def setActive(self, on=True):
    camRack.setActive(self, on=on)
    if not on:
      if self.tracker._trkival: self.tracker._trkival.finish()

  #----------------------------------------------------
  #
  def trackTo(self, nodetotrack=None):
    self.tracker.setTarget(nodetotrack)

  #----------------------------------------------------
  #
  def update(self, task=None):
    self.tracker.update(force=True)
    if task: return task.again

#========================================================================
#
class camSecurity(camRack):
  """
  """
  def __init__(self, anglespan=45, **keys):
    camRack.__init__(self, polltime=5.0, **keys)
    self._angles=[self._hpr[0]-(anglespan/2.0), self._hpr[0]+(anglespan/2.0)]
    self._angletoggle=0
    self._anglespan=anglespan
    self._rotspeed=5.0*math.atan(anglespan)
    self._trkival=LerpHprInterval(
      nodePath=base.camera, duration=self._rotspeed, hpr=base.camera.getHpr()
    )

  #----------------------------------------------------
  #
  def setActive(self, on=True):
    camRack.setActive(self, on=on)
    if not on:
      if self._trkival: self._trkival.finish()

  #----------------------------------------------------
  #
  def update(self, task=None):
    if not self._trkival.isPlaying():
      self._angletoggle=(self._angletoggle+1)%2
      h=self._angles[self._angletoggle]
      self._trkival.setStartHpr(base.camera.getHpr())
      self._trkival.setEndHpr((h,self._hpr[1],self._hpr[2]))
      self._trkival.start()
    if task: return task.again

#========================================================================
#
class camFps(camRack):
  """
  """
  def __init__(self, pivot=None, **keys):
    camRack.__init__(self, polltime=.05, **keys)
    self._freeView=0
    self._mpos=[0,0]
    self._do=DirectObject()
    self._do.accept('mouse2', self._setFreeView,[True])
    self._do.accept('mouse2-up', self._setFreeView,[False])

  #----------------------------------------------------
  #
  def _setFreeView(self, value):
    self._mpos=[base.win.getPointer(0).getX(), base.win.getPointer(0).getY()]
    self._freeView=value

  #----------------------------------------------------
  #
  def setActive(self, on=True):
    camRack.setActive(self, on=on)

  #----------------------------------------------------
  #
  def update(self, task=None):
    if self._freeView:
      newpos=[base.win.getPointer(0).getX(), base.win.getPointer(0).getY()]
      minc=[newpos[0]-self._mpos[0], newpos[1]-self._mpos[1]]
      if minc[0]+minc[1]:
        self._mpos=newpos
        hpr=base.camera.getHpr()
        base.camera.setHpr(
          hpr[0]-(minc[0]*.048),
          hpr[1]-(minc[1]*.04),
          hpr[2]
        )
    if task: return task.again

#========================================================================
#
class Tracker(object):
  """ tracker device - used to smoothly follow the heading of a node according to the position of another moving node target
  """
  #---------------------------------------------------
  #
  def __init__(self, parent=None, target=None, rotspeed=1.0):
    self._parentNP=None
    self.rotspd=rotspeed

    # this could also be an external nodepath to manage directly
    self._target=self.loadNode("trkTgt%s"%hex(id(self)), Point3(0, 0, 0))
    self._target_prepos=self._target.getPos()
    # this is an internal object used as a shadow for the parentNP motion
    self._pivot=self.loadNode("trkPvt%s"%hex(id(self)), Point3(0, -1, 1))

    if target: self.setTarget(target)
    self.reparentTo(parent)

    self._trkival=None

  #---------------------------------------------------
  #
  def setTarget(self, value):
    if value: self._target=value
    else:
      # assume it certainly exists somewhere in the tree
      self._target=base.render.find("**/trkTgt%s"%hex(id(self)))
      #reset his default parenting
      self._target.reparentTo(base.render)

  #---------------------------------------------------
  #
  def loadNode(self, name, pos=Point3(0,0,0)):
    node=base.render.attachNewNode(name)
    if pos != None: node.setPos(pos)
    return node

  #---------------------------------------------------
  #
  def reparentTo(self, parent):
    self._parentNP=parent
    if self._parentNP:
      # from now on the parent will be under the tracker pivot control
      self._pivot.setMat(self._parentNP.getMat())
    else: self._pivot=None

  #---------------------------------------------------
  #
  def target_moved(self):
    if self._target_prepos <> self._target.getPos():
      self._target_prepos=self._target.getPos()
      return True
    else: return False

  #---------------------------------------------------
  #
  def update(self, force=False):
    if self.target_moved() or force:
      self._pivot.setMat(self._parentNP.getMat())
      self._pivot.lookAt(self._target.getPos())

      if not self._trkival:
        self._trkival=LerpHprInterval(
          self._parentNP, 2.0/self.rotspd+.1, self._pivot.getHpr()
        )
      else:
        self._trkival.setStartHpr(self._parentNP.getHpr())
        self._trkival.setEndHpr(self._pivot.getHpr())
      self._trkival.start()
