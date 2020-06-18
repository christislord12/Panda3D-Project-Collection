# -*- coding: utf-8 -*-
"""
Base class for simple gamelogic.
Subclass gameLogic01 to set custom menus, splash screen etc... passing as a parameter a gameplay class, subclassed as well to have a custom gameplay.

@author: fabius
@copyright: fabius@2010
@license: GCTA give credit to (the) authors
@version: 0.1
@date: 2010-09
@contact: astelix (U{panda3d forums<http://www.panda3d.org/forums/profile.php?mode=viewprofile&u=752>})
@status: eternal WIP

@todo:
aggiungere un terzo slide oltre titologame e scores di spiega del game (o meglio metterlo in gameplay? magari per ora solo immagini) e/o fare una voce di menu' HELP

@note:
  - FSM mechanic:
    - a) call a request 'X'
    - b) FSM status goes to 'X' either if we specified enterX and filterX (respectively) methods or not, otherwise it will fall in the default methods
    - c) stay cool in the last filterX method, waiting another different request and when it comes:
      - will be summoned the eventual exitX method or the default one and then again b)

@warning: in this stuff will interact different input layers with FSM. That could be problematic so we gotta enable/disable the inputs passing fom FSM to other not FSM-driven pieces of code
"""
import os, random, sys
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from direct.fsm import FSM
from direct.gui.OnscreenText import OnscreenText
from dgstuff import *
import scorer

#=========================================================================
#
class gameLogic01(ShowBase, FSM.FSM):
  _DEBUG=False
  def __init__(self, gameplay, settings={}):
    """
    """
    ShowBase.__init__(self)
    FSM.FSM.__init__(self, 'fsm_%r'%id(self))

    self.gameplay=gameplay
    self._backto=[]
    self._menuqueue=[]
    self.playername="Player1"
    self.titledata=None
    self.splashfile='data/textures/splash.png'
    #** used to carry and pass around the gameplay settings
    self.gamesettings={
      'playernames': ['cpu', self.playername],
      'opponent': 'cpu',
    }
    self.gamesettings.update(settings)
    #
    self.setinputs()
    #
    self._loadguidata()
    #
    self.request('Title')
  #
  #
  def setinputs(self, on=True):
    """ FSM keyboard inputs
    @note: with this we'll define all the FSM states inputs once for all - if an input is not used will fall in the default, safely unmanaged
    """
    allinputs={
      'tab': 'advance', 'shift-tab': 'back',
      'enter': 'select', 'escape': 'quit',
      'arrow_down': 'down', 'arrow_left': 'left', 'arrow_up': 'up',
      'arrow_right': 'right',
    }
    for k,v in allinputs.items():
      if on: self.accept(k, self.request, [v])
      else: self.ignore(k)

  #-----------------------------------------------------
  #
  _currenttune=-1
  _tunes=[]
  _tunesfolder="./data/sounds/music/"
  playingtune=None
  def playtune(self, tunetoplay=""):
    """ Helper to play sounds
    """
    self._tunes=self.walktree(self._tunesfolder)
    if len(self._tunes):
      # if no tune specified will be played the next one in the list
      if not tunetoplay:
        self._currenttune=(self._currenttune+1 if
          (self._currenttune+1) < len(self._tunes) else 0
        )
        tunetoplay=self._tunes[self._currenttune]
      if (self.istuneplaying()): self.playingtune.stop()
      self.playingtune = self.loader.loadSfx(tunetoplay)
      self.playingtune.setLoop(False)
      self.playingtune.play()

  def istuneplaying(self):
    return (self.playingtune and
      (self.playingtune.status() == self.playingtune.PLAYING)
    )

  #-----------------------------------------------------
  #
  def walktree(self, top, ext='.ogg'):
    l=[]
    for f in os.listdir(top):
      pathname = os.path.join(top, f)
      if os.path.isfile(pathname) and os.path.splitext(pathname)[1] == ext:
        l.append(pathname)
    l.sort()
    return l

  #-----------------------------------------------------
  #
  #** default FSM REQUEST - here will fall unintercepted requests
  #def defaultEnter(self, *args):
    #print "[DEF]entering '%s' from '%s'..." % (self.newState, self.oldState)
  def defaultFilter(self, request, args):
    if request == 'quit':
      ###print "[DEF] routing request '%s' to Menu" % request
      return ('Menu', self.menu_main)
    else:
      ###print "[DEF] unhandled filter request '%s'" % request
      return FSM.FSM.defaultFilter(self, request, args)
  #def defaultExit(self):
    #print "[DEF]exiting from '%s' to '%s'..." % (self.oldState, self.newState)

  #-----------------------------------------------------
  #
  #** TITLE FSM REQUEST
  def enterTitle(self, *args):
    self.dbgprint("[Title] entering")
    self._title=gametitle(
      self, top10data=self.titledata, splashfile=self.splashfile
    )
    if (not self.istuneplaying()): self.playtune()

  def filterTitle(self, request, args):
    self.dbgprint("[Title] filtering (%s)"%request)
    if request in ['advance', 'select']: return 'Gameplay'
    else: return self.defaultFilter(request, args)

  def exitTitle(self):
    self.dbgprint("[Title] exiting")
    self._title.finish()
    del self._title

  #-----------------------------------------------------
  """ methods for the menu ovelapping mechanic to manage the add/remove of gui controls like menus etc.
  """
  #** add a menu over
  def push_menu(self, menudata):
    if len(self._menuqueue): self._menuqueue[-1].pause()
    self._menuqueue.append(dgmenu(menudata))
  #** add an entry control
  def push_entry(self, menudata):
    if len(self._menuqueue): self._menuqueue[-1].pause()
    self._menuqueue.append(dginput(menudata))
  #** to remove topmost control
  def pop_menu(self, foo=None): self.request('_menuend')

  #-----------------------------------------------------
  # initialise menus and such (override it)
  def _loadguidata(self): pass

  #-----------------------------------------------------
  #
  #** MENU FSM REQUEST
  def enterMenu(self, *args):
    self.dbgprint("[Menu] entering")
    # turning off all inputs here - we listen just the menu
    self.setinputs(False)
    self._backto.append(self.oldState)
    #args[0]=menu to load
    self.push_menu(args[0])

  #**
  def filterMenu(self, request, *args):
    self.dbgprint("[Menu] filtering (%s)"%request)
    if request == '_menuend':
      menu=self._menuqueue.pop()
      menu.finish()
      if len(self._menuqueue): self._menuqueue[-1].play()
      else:
        # when the root menu close we drive back to the caller state
        bt=self._backto.pop()
        self.dbgprint("Menu: back to old:%s" % bt)
        return bt
    else: return self.defaultFilter(request, args)

  #**
  def exitMenu(self):
    # cleaning if exiting menu state abruptedly
    self.dbgprint("[Menu] exiting")
    self.setinputs()
    self._backto=[]
    for menu in self._menuqueue:
      menu.finish()
    self._menuqueue=[]

  #-----------------------------------------------------
  #
  #** GAMEPLAY FSM REQUEST
  gameplayshell=None
  # override eventually
  def postgameover(self, score=None): return None

  def abortgame(self, foo=None):
    #self.gameplayshell.pause(0)
    if self.gameplayshell:
      self.dbgprint("abort game")
      self.gameplayshell.finish()
      self.gameplayshell=None
    self.request('Title')

  def enterGameplay(self, *args):
    """ will enter here after 'Gameplay' FSM request.
    Will be evaluated here the gameplay status and eventually the game will be paused/restarted.
    """
    self.dbgprint("[Gameplay] entering")
    if self.gameplayshell:
      self.dbgprint("returning off menu")
      self.gameplayshell.pause(0)
    else:
      self.dbgprint("Starting new game")
      if (self.istuneplaying()): self.playingtune.stop()

      self.gameplayshell=self.gameplay(
        self, settings=self.gamesettings,
        callback=lambda arg: taskMgr.doMethodLater(
          5, self.postgameover, '_pogaov',[arg]
        )
      )

  def filterGameplay(self, request, args):
    """
    @note: 'quit' request here will just pause the game, therefore the 'Menu' request must be called explicitly
    """
    self.dbgprint("[Gameplay] filtering (%s)"%request)
    if request == 'quit':
      self.gameplayshell.pause(1)
      return 'Menu', self.menu_stopgame
    else:
      return self.defaultFilter(request, args)

  def exitGameplay(self):
    self.dbgprint("[Gameplay] exiting")

  #-----------------------------------------------------
  #
  def dbgprint(self, msg):
    if self._DEBUG: print msg

#=========================================================================
#
class gametitle(object):
  """
  The game presentation class.
  Usually shows a splash screen, the scoreboard and help pages (in the future maybe).
  """
  def __init__(
    self, parent, top10data=None, splashfile='data/textures/splash.png'
  ):
    self.parent=parent
    if top10data:
      self._top10sb=scorer.scorer(filename=top10data['scorefile'], clamp=10)
      fs="%%0%dd"%top10data.get('scoredigits',3)
      items=[
        [
          {'label': line[1].strip()}, {'label': fs%line[0]}
        ] for line in self._top10sb.getscores()
      ]
      top10data['items']=items
      top10data['visible']=False
      self.top10table=dgtable(top10data)
    else: self.top10table=None
    self.splash=OnscreenImage(
      parent= self.parent.render2d, image = splashfile
    )
    self._setsplash()

  #-----------------------------------------------------
  #
  def finish(self):
    self.splash.destroy()
    if self.top10table:
      taskMgr.remove('gametitletsk')
      self.top10table.finish()

  #-----------------------------------------------------
  #
  def _setsplash(self, *args):
    if self.top10table:
      taskMgr.remove('gametitletsk')
      self.top10table.canvas.hide()
      self.splash.show()
      taskMgr.doMethodLater(5, self._settop10, 'gametitletsk')

  #-----------------------------------------------------
  #
  def _settop10(self, *args):
    taskMgr.remove('gametitletsk')
    self.splash.hide()
    taskMgr.doMethodLater(8, self._setsplash, 'gametitletsk')
    self.top10table.canvas.show()

#=========================================================================
#
class gameplaybase(DirectObject):
  """ To make a custom game, fist start subclassing this.
  """
  _DEBUG=True
  _SETTINGS={
    'opponent': 'human',
    'playernames': ['CPU0', 'Player1']
  }
  #-----------------------------------------------------
  #
  def __init__(self, parent, settings=_SETTINGS, callback=None):
    self._SETTINGS.update(settings)
    self.parent=parent
    self.gameovercallback=callback

    self.setscene()
    self.setcamera()
    self.setinputs()
    self.setgame()
    self.loadeffects()

  #-----------------------------------------------------
  # to be overriden
  def setcamera(self): pass
  def setinputs(self): pass
  def setscene(self): pass
  def setgame(self): pass
  def onfinish(self): pass

  #-----------------------------------------------------
  #
  _effects={}
  _effectsfolder="./data/sounds/effects/"
  def loadeffects(self):
    self._effects=self.walktree(self._effectsfolder)

  def playeffect(self, name):
    if name in self._effects:
      self._effects[name].play()

  #-----------------------------------------------------
  #
  def walktree(self, top, ext='.ogg'):
    d={}
    for f in os.listdir(top):
      pathname = os.path.join(top, f)
      if os.path.isfile(pathname) and os.path.splitext(pathname)[1] == ext:
        d[os.path.splitext(f)[0]]=self.parent.loadSfx(pathname)
    return d

  #-----------------------------------------------------
  #
  def finish(self):
    # @attention: self.startclock() call is very important cos if we paused the game before, all the application hangs therefore everything outside the game will be freezed as well.
    self.startclock()
    self.ignoreAll()
    for tsk in taskMgr.getTasksMatching('gpl01_*'): taskMgr.remove(tsk)
    self.onfinish()
  #-----------------------------------------------------
  #
  _GCLK=None
  _FT=None
  def startclock(self):
    if self._GCLK and self._FT:
      self._GCLK.setRealTime(self._FT)
      self._GCLK.setMode(ClockObject.MNormal)
      self.parent.enableParticles()
      self._GCLK=None
      self.dbgprint("[gpl01] restarting...")

  def stopclock(self):
    if not self._GCLK:
      self.dbgprint("[gpl01] pausing...")
      self.parent.disableParticles()
      self._GCLK=ClockObject.getGlobalClock()
      self._FT=self._GCLK.getFrameTime()
      self._GCLK.setMode(ClockObject.MSlave)

  def pause(self, force=None):
    if (self._GCLK == None) or (force == 1): self.stopclock()
    elif self._GCLK or (force == 0): self.startclock()

  #-----------------------------------------------------
  #
  def dbgprint(self, msg):
    if self._DEBUG: print msg

#=========================================================================
#
if __name__ == "__main__":
  loadPrcFileData("", """win-size 800 600
  win-origin 0 0
  model-path $MAIN_DIR/data/models/
  sync-video 0
  #show-frame-rate-meter #t
  """
  )

  """ Sample to show how to subclass the parent gamelogic class to have a functional game mechanic
  """
  class myGame(gameLogic01):
    def __init__(self, gameplay):
      gameLogic01.__init__(self, gameplay)
      self.gamesettings['mode']='2d'

    #** manages what happens as the game ends
    def postgameover(self, score=None):
      self.dbgprint("Score report after gameover:\n%r"%score)
      if score['opponent'] == 'cpu':
        sc=scorer.scorer(filename='pong.sco')
        sc.putscore(self.playername, score['value'])
      self.abortgame()
      return None

    def _setplayername(self, v):
      if v.strip():
        self.playername=v
        self.gamesettings['playernames'][1]=self.playername

    def _loadguidata(self):
      #** splash screen plus top-10 table
      self.titledata={'scorefile': 'gameplay01.sco', 'scoredigits': 6,
        'title': '** TOP 10 SCORES **', 'titlescale': .09,
        'scale':(1.5, 1.1), 'itemsvisible':10, 'margin': (.1,.15),
        'texture':'data/models/textures/menu_pong.png',
        'textfont': loader.loadFont("data/fonts/slkscre.ttf"),
        'itemswidth': (.9, .4), 'itemsscale':.07,
        'head': [
          { 'label': 'Player', 'color':(1,1,1,1), 'textscale':.09},
          { 'label': 'Score', 'color':(1,1,1,1), 'textscale':.09},
        ],
      }

      def menumerge(a, intob):
        r=intob.copy()
        r.update(a)
        return r
      #** common parameters for all menus - will be merged with each specific menu
      menucommon={'scale':(1.1, .6), 'titlescale':.1,  'pos':(0,0),
        'texture':'data/models/textures/menu_pong.png',
        'titlecolor': (1,1,1,1), 'itemscolor': (1,1,1,1), 'itemsscale': .08,
        'highlightcolor':(0,0,0,1),
        'textfont': loader.loadFont("data/fonts/slkscre.ttf"),
      }
      #** quitgame
      menu={'title': 'Sure to quit?', 'selected':1,
        'items': [
          {'label': 'Yes', 'callback': sys.exit},
          {'label': 'No', 'callback': self.pop_menu},
        ],
        'exit': self.pop_menu,
      }
      self.menu_quitgame=menumerge(menu, menucommon)
      #** player name
      def menu_name():
        # e' in forma di funza perche' playername puo' cambiare
        menu={
          'align': 'center',
          'title': 'Put Your Name', 'scale': (1.2,.6), 'margin':(.07, .05),
          'titlecolor': (1,1,1,1),
          'initialtext': self.playername, 'inputscale': .07, 'inputwidth': 25,
          'inputcolor':(0,0,0,1), 'callback': lambda v: self._setplayername(v),
          'exit': self.pop_menu, 'autoexit': True,
        }
        return menumerge(menu, menucommon)
      #** main menu
      menu={'title': 'MAIN MENU',
        'items': [
          {'label': 'Player Name',
            'callback': lambda foo=None: self.push_entry(menu_name()),
          },
          {'label': 'Exit Game',
            'callback': lambda foo=None: self.push_menu(self.menu_quitgame),
          },
        ],
        'exit': self.pop_menu,
      }
      self.menu_main=menumerge(menu, menucommon)
      #** used in gameplay request
      menu={'title': 'Stop playing?', 'selected': 1, 'scale':(1.2, .5),
        'items': [
          {'label': 'Yess', 'callback': self.abortgame, },
          {'label': 'Nope', 'callback': self.pop_menu, },
        ],
        'exit': self.pop_menu,
      }
      self.menu_stopgame=menumerge(menu, menucommon)

  from pong3dgpl import gameplay
  game=myGame(gameplay)
  run()
