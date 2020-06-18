# -*- coding: utf-8 -*-
"""
Input helper to ease the input setup

@author: fabius
@copyright: fabius@2010
@license: GCTA give credit to (the) authors
@version: 0.1
@date: 2010-06
@contact: astelix (U{panda3d forums<http://www.panda3d.org/forums/profile.php?mode=viewprofile&u=752>})
@status: eternal WIP

@todo:
  - introdurre bind/unbind dinamico dei controlli o di singoli input
"""
__all__ = ['easyinput']

from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
import sys
from pandac.PandaModules import WindowProperties

#================================================================
#
try:
  import pygame as PYG
  PYG.init()
except ImportError:
  print "[WARNING] Pygame module not present"
  PYG=None

class easyinput(DirectObject):
  """
  A class to ease the input bind of actions.
  Setup:
    - define a config string similar to what we find in a quake config file, where a bind command assign a keyword to an input device event to act as a bridge between the device input and the game action handler
    - define a dictionary with the config keywords as keys and the handlers as values
  """
  _DEBUG=False
  #------------------------------------------------------
  #
  # predefined bind names/named-handlers; you may change'em passing an overrider config text overrider
  DEFAULT_CONFIG="""
//JOY ------
bind joy0-button1 "action"
//+- y axis movement : by default will fire forward/back events
bind joy0-axis1 "thrust"
bind joy0-button2 "jump"
//+- x axis movement : by default will fire moveleft/moveright events
bind joy0-axis0 "heading"
bind joy0-button11 "quit"
bind joy0-button6 "run"
//KB ------
bind enter "action"
bind w "forward"
bind s "back"
bind a "left"
bind d "right"
bind arrow_down "down"
bind arrow_up "up"
bind arrow_left "left"
bind arrow_right "right"
bind rcontrol "jump"
bind page_up "headup"
bind page_down "headdown"
bind escape "quit"
bind rshift "run"
bind \ "alwaysrun"
// MOUSE ------
//to unbind some event specify an empty string as handler
bind mouse1 "mouse1"
bind mouse2 "mouse2"
bind mouse3 "mouse3"
bind mouse-x "heading"
//+- z axis movement : by default will fire headup/headdown events
bind mouse-y "pitch"
bind wheel_up "zoomin"
bind wheel_down "zoomout"
"""
  def __init__(self, config='', bridge={}, debug=False):
    """
    @param config:
      E{\}n sepatated string of 3 element lines:
      [0]=bind [1]=event name [2]=bridge keyword.
    @param bridge: dictionary of event keywordE{:}handler elements.
    """
    DirectObject.__init__(self)
    #
    self._DEBUG=debug
    #
    self.JOY=0

    # self.config={'<command>':{'<event>': <handler>}}
    self.config={}
    self.add_config(self.DEFAULT_CONFIG)
    self.add_config(config)

    # bridge with predefined events connected to handlers to be overrided
    _bridge={
      'action': self.action,
      'back': self.back,
      'forward': self.forward,
      'jump': self.jump,
      'left': self.left,
      'right': self.right,
      'thrust': self.thrust,
      'pitch': self.pitch,
      'heading': self.heading,
      'up': self.headup,
      'down': self.headdown,
      'quit': self.quitme,
      'run': self.run,
      'alwaysrun': self.alwaysrunToggle,
      'zoomin': lambda foo: self.zoom(1),
      'zoomout': lambda foo: self.zoom(-1),
    }
    # melt default bridge with user defined
    for k,v in bridge.iteritems(): _bridge[k]=v

    # returns the number of joysticks found
    self.JOY=self.pyga_joysetup()

    # bind operations happens here
    self.readmouse_binds={}
    readmouse={}
    for evt, hndrepeat in self.config['bind'].iteritems():
      hnd,repeat=hndrepeat
      if hnd in _bridge:
        hname=_bridge[hnd]
        #bind joystick
        if evt.startswith('joy'):
          if self.JOY:
            ###print ">>>JOaccept:%s->%s" % (evt, hname)
            self.accept(evt, _bridge[hnd])
        #bind mouse
        elif evt.startswith('mouse'):
          # if there is a bind for mouse movement will be created relative listeners to hear mouse-x or mouse-y events fired by a mouse polling task eventually created below
          if evt in ["mouse-x", "mouse-y"]:
            readmouse[evt]=_bridge[hnd]
          else:
            #here should bind button listeners, but not necessarily
            ###print ">>>MOaccept:%s->%s" % (evt, hname)
            self.accept(evt, _bridge[hnd], [1])
            self.accept(evt+"-up", _bridge[hnd], [0])
        # qui dovrebbe arrivare solo kbkey
        else:
          ###print ">>>KBaccept:%s->%s" % (evt, hname)
          repeat='-repeat' if repeat else ''
          self.accept(evt+'-up', _bridge[hnd], [0])
          self.accept(evt+repeat, _bridge[hnd], [1])

    #** spawn the mouse movement tracking task (see above the mouse bind part)
    self.mouseTask=None
    if readmouse: self.set_mouse_read(readmouse, True)
    #taskMgr.popupControls()
    ###print messenger
    self.pyga_joytask=None

  #------------------------------------------------------
  #
  def finish(self):
    """ Invoke this before this class object will be off duty """
    self.ignoreAll()
    if self.mouseTask:
      taskMgr.remove(self.mouseTask)
      self.mouseTask=None
    if self.pyga_joytask:
      taskMgr.remove(self.pyga_joytask)
      self.pyga_joytask=None
    props = WindowProperties()
    props.setCursorHidden(False)
    props.setMouseMode(WindowProperties.MAbsolute)
    base.win.requestProperties(props)

  #------------------------------------------------------
  #
  def set_mouse_read(self, readmouse, activate):
    if self.mouseTask:
      taskMgr.remove(self.mouseTask)
      self.mouseTask=None

    if activate:
      if not self.readmouse_binds:
        for xy in ['mouse-x', 'mouse-y']:
          self.readmouse_binds[xy]=readmouse.get(xy, self._foo)
      taskName = "_esnptmo-%s" % id(self)
      self.mouseTask = taskMgr.add(self._read_mouse, taskName, sort=40)

    props = WindowProperties()
    props.setCursorHidden(activate)
    props.setMouseMode(
      [WindowProperties.MAbsolute, WindowProperties.MRelative][activate])
    base.win.requestProperties(props)

  #------------------------------------------------------
  #
  # to avoid to flood with useless still mouse events
  _pre_mox=0
  _pre_moy=0
  mouse_speed_factor=5.
  def _read_mouse(self, task):
    """Read the mouse position and then route mouse position to the relative binded handler
    """
    if base.mouseWatcherNode.hasMouse():
      x = base.win.getPointer(0).getX()
      y = base.win.getPointer(0).getY()
      deltax=(x-self._pre_mox)
      deltay=(y-self._pre_moy)
      if deltax or deltay:
        self.readmouse_binds["mouse-x"](deltax/self.mouse_speed_factor)
        self.readmouse_binds["mouse-y"](deltay/self.mouse_speed_factor)
        self._predelta=True
      elif self._predelta:
        self._predelta=False
        self.readmouse_binds["mouse-x"](0)
        self.readmouse_binds["mouse-y"](0)
      self._pre_mox,self._pre_moy=(x, y)
    else:
      self.readmouse_binds["mouse-x"](0)
      self.readmouse_binds["mouse-y"](0)

    return Task.cont

  #------------------------------------------------------
  #
  def _foo(self, foo): pass
  #------------------------------------------------------
  #
  def add_config(self, config):
    """Merge a text file config in the main config data collector where the latter override the former
    """
    clean=lambda n: n.strip().strip('"').lower()
    for line in config.split('\n'):
      items=line.strip().split()
      if items and len(items) >= 3:
        cmd, evt, hnd=items[:3]
        """ NOTE
          - just 'bind' command expected right now
          - '+' prepended ti the handler means REPEAT (make sense just for keyboard keys actually)
        """
        cmd=clean(cmd)
        if cmd in ['bind']:
          evt,hnd=(clean(evt), clean(hnd))
          if not cmd in self.config: self.config[cmd]={}
          repeat=hnd.startswith('+')
          if repeat: hnd=hnd[1:]
          self.config[cmd].update([[evt, [hnd, repeat]]])

  #------------------------------------------------------
  #
  def pyga_joysetup(self):
    """Pygame joystick(s) startup - returns the number of joysticks found
    """
    jcount=0
    if PYG:
      self.dbgprint("pygame starts")
      jcount=PYG.joystick.get_count()
      if jcount > 0:
        for x in range(jcount):
          j = PYG.joystick.Joystick(x)
          j.init()
          self.dbgprint(">>>Enabled joystick: %s" % j.get_name())
        taskMgr.add(self.pyga_joytask, 'tsk_pygajoy')
      else:
        self.dbgprint("No Joysticks to Initialize!")

    return jcount
  #------------------------------------------------------
  #
  def pyga_joytask(self, task):
    """If there is a joy event it will be sent a proper string message and event value to the messenger queue
    """
    for e in PYG.event.get():
      # joystick buttons up and down events routing
      # will send a string like, i.e.: "joy0-button1" for the button 1 of the joy 0 and 0 or 1 as a parameter for button up or down status respectively
      if e.type in [PYG.JOYBUTTONDOWN, PYG.JOYBUTTONUP]:
        s="joy%d-button%d" % (e.joy, e.button)
        messenger.send(s, [1 if e.type == PYG.JOYBUTTONDOWN else 0])
      # joistick axis (analog and digital)
      # will send a string like, i.e.: "joy0-axis1" for the axis 1 of the joy 0 and a number between 0 and 1 or 0 and -1 as the stick or hat status (the digital stick returns 0 OR +-1 but analog sticks floating values from 0.0 and +-1.0)
      elif e.type == PYG.JOYAXISMOTION:
        s="joy%d-axis%d" % (e.joy, e.axis)
        ###print "Jax-%r(%r)" % (e.axis, e.value)
        if e.axis in [1,2]:
          messenger.send(s, [-e.value])
        else:
          messenger.send(s, [e.value])
    return Task.cont
  #-----------------------------------------------------
  #
  def dbgprint(self, msg):
    if self._DEBUG: print msg
  #------------------------------------------------------
  # PREDEFINED INPUT EVENT HANDLERS (to override)
  """
  NOTE some events are grouped in one such us thrust collect forward and back events so that you may subclass just thrust and ease your game logic
  """
  #------------------------------------------------------
  #
  def action(self, evt=None):
    """evt=0 or 1"""
    self.dbgprint("action(%r)"%evt)
  #------------------------------------------------------
  #
  def alwaysrunToggle(self, evt=None):
    """evt=0 or 1"""
    self.dbgprint("alwaysrun(%r)"%evt)
  #------------------------------------------------------
  #
  def back(self, evt=None):
    """evt=0 to 1"""
    self.thrust(-evt)
  #------------------------------------------------------
  #
  def forward(self, evt=None):
    """evt=0 to 1"""
    self.thrust(evt)
  #------------------------------------------------------
  #
  def jump(self, evt=None):
    """evt=0 or 1"""
    self.dbgprint("jump(%r)"%evt)
  #------------------------------------------------------
  #
  def heading(self, evt=None):
    """evt=-1. to 1. - for x movements
    to use for steering
    """
    self.dbgprint("heading(%r)"%evt)
  #------------------------------------------------------
  #
  def headup(self, evt=None):
    """evt=0 to 1"""
    self.pitch(evt)
  #------------------------------------------------------
  #
  def headdown(self, evt=None):
    """evt=0 to 1"""
    self.pitch(-evt)
  #------------------------------------------------------
  #
  def left(self, evt=None):
    """evt=0 to 1"""
    self.dbgprint("moveleft(%r)"%evt)
  #------------------------------------------------------
  #
  def right(self, evt=None):
    """evt=0 to 1"""
    self.dbgprint("moveright(%r)"%evt)
  #------------------------------------------------------
  #
  def pitch(self, evt=None):
    """evt=-1. to 1. - for z movements
    by default the evt collect headup and headdown events
    override or bind this in your subclass
    """
    self.dbgprint("pitch(%r)"%evt)
  #------------------------------------------------------
  #
  def quitme(self, evt=None):
    """evt=0 or 1"""
    if evt: self.dbgprint("quitting...")
  #------------------------------------------------------
  #
  def run(self, evt=None):
    """evt=0 or 1"""
    self.dbgprint("run(%r)"%evt)
  #------------------------------------------------------
  #
  def thrust(self, evt=None):
    """evt=-1. to 1. - for y movements
    by default the evt collect forward and back events
    override or bind this in your subclass
    """
    self.dbgprint("thrust(%r)"%evt)
  #------------------------------------------------------
  #
  def zoom(self, evt=None):
    self.dbgprint("z00ming(%r)"%evt)

#================================================================
#
if __name__ == '__main__':
  import direct.directbase.DirectStart
  from direct.gui.DirectGui import *
  from direct.gui.OnscreenText import OnscreenText

  #============================================================
  #
  text2d=lambda line=0, text='': OnscreenText(
      text = text, pos = (0, line*.1), scale = 0.05, mayChange=True, fg=(1,1,0,1), bg=(0,0,0,.5)
    )
  class instanced(DirectObject):
    """Sample use of easyinput class
    in brief you define a text very similar to quake .cfg files strings where to issue a bind command followed by a input event name and a keyword that define a bridge between the input event and a handler that will be called when that event will be fired
    """
    #------------------------------------------------------
    #
    def __init__(self):
      DirectObject.__init__(self)
      #
      #self.accept('escape-up', self.quitme)
      # crea ost di debug
      self.display={}
      l=0
      for x in ['joy', 'mouse', 'kb', 'unspecified']:
        l+=1
        self.display[x]=text2d(line=l, text=x.upper()+":")
      ###
      # bind eventi device di input
      #file.cfg tipo quake3
      cfg="""//JOY ------
  bind joy0-button9 "quit" // a comment
  bind joy0-button1 "action"
  bind joy0-axis1 "axis1"
  //KB ------
  bind arrow_up "forward"
  bind escape "quit"
  bind enter "action"
  // MOUSE ------
  bind mouse1 "action"
  """
      #these are the allowed handlers we need
      hndbridge={
        'axis1': self.axis1test,
        'action': self.allaction,
        'quit': self.quitme,
      }
      #
      self.xinput=easyinput(cfg, hndbridge)
    #------------------------------------------------------
    #
    def quitme(self, evt=None):
      """qui ci si aspetta un evt click (evt=true)"""
      if evt:
        self.dbgprint("too much for testing: so-long")
        sys.exit()
    #------------------------------------------------------
    #
    def axis1test(self, evt=None):
      self.display['joy'].setText("JOY:%r"%evt)
    #------------------------------------------------------
    #
    def allaction(self, evt=None):
      self.display['unspecified'].setText("(action):%r"%evt)

  #============================================================
  #
  class derived(easyinput):
    """sample usage of easyinput class as derived clas
    """
    #------------------------------------------------------
    #
    def quitme(self, evt=None):
      """overrided method from the base class"""
      if evt:
        self.dbgprint("bye!")
        sys.exit()
  #
  # the test menu
  #
  def setchoice(choice):
    DO.ignore('1')
    DO.ignore('2')
    DO.ignore('escape')
    x=choice.strip()
    if x in ['1', '2']:
      if x == '1':
        app = instanced()
      else:
        DO.ignore('escape')
        app = derived()

  DO=DirectObject()
  DO.accept('1', setchoice, ['1'])
  DO.accept('2', setchoice, ['2'])
  DO.accept('escape', sys.exit)

  text = """
  Sample choice
  =============
  1) Instanced easyInput class
  2) Derived class from easyInput
  ESC) exit
  """
  menu = OnscreenText(parent=base.a2dTopLeft,
    text = text, pos = (.5, -.1), scale = 0.05, mayChange=False,
    fg=(1,1,0,1), bg=(0,0,0,.5)
  )

  run()

