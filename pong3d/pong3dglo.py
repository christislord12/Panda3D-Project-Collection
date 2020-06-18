# -*- coding: utf-8 -*-
""" Pong3d gamelogic module.
This define the root of what will run as a whole game, with the aid of other modules. Check the help for some insight of this project.

Gameplay: press SPACEBAR to launch the ball, move the mouse (recommended) or use the WASD or the arrow keys or even the joystick to move the pad. A game is won by the player who  wins 2 sets more than his foe. Each set is won by the player who wons 3 rallies but gotta win 2 rallies more than his foe in case of tie score.

@author: fabius
@copyright: fabius@2010
@license: GCTA give credit to (the) authors
@version: 0.1
@date: 2010-09
@contact: astelix (U{panda3d forums<http://www.panda3d.org/forums/profile.php?mode=viewprofile&u=752>})
@status: eternal WIP
@todo:
 - spiega gameplay (ENG)
@newfield credits: Credits
@credits:
  - 8BITMUSIC credits:
      - U{a few years later<http://www.8bitpeoples.com/discography/by/minusbaby>}
      - U{same thing<http://www.8bitpeoples.com/discography/by/8gb>}
      - U{chiprape<http://www.8bitpeoples.com/discography/by/stu>}

G{classtree myGame}
"""

import sys
from pandac.PandaModules import WindowProperties
from gamelogic01 import gameLogic01
from pandac.PandaModules import loadPrcFileData
import scorer
loadPrcFileData("", """win-size 800 600
win-origin 0 0
model-path $MAIN_DIR/data/models/
sync-video 0
#show-frame-rate-meter #t
"""
)

#=========================================================================
class myGame(gameLogic01):
  """
  Pong game logic derived from simple gemelogic base class.
  This is the main class, subclassed off his parent base L{gamelogic01} to have a custom game. Other classes are involved to manage menus, inputs, scores and such, and you can find all this stuff in the following files:
  L{gameLogic01.py<gamelogic01>}, L{scorer.py<scorer>}, L{dgstuff.py<dgstuff>}, L{easyinput.py<easyinput>},
  """
  GS_OPPONENTS=['human','cpu']
  GS_MODES=['3d','3dg']
  SCOREFILE='pong3d.sco'
  def __init__(self, gameplay):
    gamesettings={'mode':'3dg'}
    gameLogic01.__init__(self, gameplay, settings=gamesettings)

  #**
  def postgameover(self, score=None):
    """ manages what happens as the game ends """
    self.dbgprint("Score report after gameover:\n%r"%score)
    if score['opponent'] == 'cpu':
      sc=scorer.scorer(filename=self.SCOREFILE)
      sc.putscore(self.playername, score['value'])
    self.abortgame()
    return None

  #**
  def setvideo(self, index=None):
    """ handler called by menu_options_video """
    reso=['800x600','1024x768']
    def _setresolution(res, fullscreen=False):
        wp = WindowProperties()
        wp.setSize(int(res[0]), int(res[1]))
        wp.setFullscreen(fullscreen)
        base.win.requestProperties(wp)
    if index <> None: _setresolution(reso[index].split('x'))

  def setopponent(self, index=None):
    self.dbgprint(">>>SETTING OPPONENT %s" % self.GS_OPPONENTS[index])
    self.gamesettings['opponent']=self.GS_OPPONENTS[index]
    self.menu_options_opponent['selected']=index
    self.pop_menu()

  def setgamemode(self, index=None):
    self.dbgprint(">>>SETTING GAME MODE %s" % self.GS_MODES[index])
    self.gamesettings['mode']=self.GS_MODES[index]
    self.menu_options_mode['selected']=index
    self.pop_menu()

  def _setplayername(self, v):
    if v.strip():
      self.playername=v
      self.gamesettings['playernames'][1]=self.playername

  def _loadguidata(self):
    self.splashfile='data/textures/splashpong.png'
    self.titledata={'scorefile': self.SCOREFILE, 'scoredigits': 6,
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
    # common parameters for all menus - will be merged with each specific menu
    menucommon={'scale':(1.1, .6), 'titlescale':.1,  'pos':(0,0),
      'texture':'data/models/textures/menu_pong.png',
      'titlecolor': (1,1,1,1), 'itemscolor': (1,1,1,1), 'itemsscale': .08,
      'highlightcolor':(0,0,0,1),
      'textfont': loader.loadFont("data/fonts/slkscre.ttf"),
    }
    # video options
    menu={'title': 'Video Options',
      'callback': self.setvideo,
      'items': [
        {'label': '800x600'}, {'label': '1024x768'},
        {'label': 'back', 'callback': self.pop_menu},
      ],
      'exit': self.pop_menu,
    }
    self.menu_options_video=menumerge(menu, menucommon)

    # opponent
    menu={'title': 'Choose Opponent', 'scale':(1.2, .5),
      'selected': self.GS_OPPONENTS.index(self.gamesettings['opponent']),
      'callback': self.setopponent,
      'items': [
        {'label': 'Human'},
        {'label': 'CPU'},
        {'label': 'back', 'callback': self.pop_menu},
      ],
      'exit': self.pop_menu,
    }
    self.menu_options_opponent=menumerge(menu, menucommon)
    # game-mode
    menu={'title': 'Game Mode', 'scale':(1.2, .5),
      'selected': self.GS_MODES.index(self.gamesettings['mode']),
      'callback': self.setgamemode,
      'items': [
        {'label': '3D'},
        {'label': '3D googles'},
        {'label': 'back', 'callback': self.pop_menu},
      ],
      'exit': self.pop_menu,
    }
    self.menu_options_mode=menumerge(menu, menucommon)
    # options
    menu={'title': 'Options',
      'items': [
        {'label': 'video',
          'callback': lambda foo=None: self.push_menu(self.menu_options_video),
        },
        {'label': 'opponent',
          'callback': lambda foo=None:
            self.push_menu(self.menu_options_opponent),
        },
        {'label': 'game mode',
          'callback': lambda foo=None:
            self.push_menu(self.menu_options_mode),
        },
        {'label': 'back', 'callback': self.pop_menu},
      ],
      'exit': self.pop_menu,
    }
    self.menu_options=menumerge(menu, menucommon)
    # quitgame
    menu={'title': 'Sure to quit?', 'selected':1,
      'items': [
        {'label': 'Yes', 'callback': sys.exit},
        {'label': 'No', 'callback': self.pop_menu},
      ],
      'exit': self.pop_menu,
    }
    self.menu_quitgame=menumerge(menu, menucommon)
    # player name
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
    # main menu
    menu={'title': 'MAIN MENU',
      'items': [
        {'label': 'Options',
          'callback': lambda foo=None: self.push_menu(self.menu_options),
        },
        {'label': 'Player Name',
          'callback': lambda foo=None: self.push_entry(menu_name()),
        },
        {'label': 'Exit Game',
          'callback': lambda foo=None: self.push_menu(self.menu_quitgame),
        },
        {'label': 'Back', 'callback': self.pop_menu,},
      ],
      'exit': self.pop_menu,
    }
    self.menu_main=menumerge(menu, menucommon)
    # used in gameplay request
    menu={'title': 'Stop playing?', 'selected': 1, 'scale':(1.2, .5),
      'items': [
        {'label': 'Yess', 'callback': self.abortgame, },
        {'label': 'Nope', 'callback': self.pop_menu, },
      ],
      'exit': self.pop_menu,
    }
    self.menu_stopgame=menumerge(menu, menucommon)

#=========================================================================
#
if __name__ == "__main__":
  from pong3dgpl import gameplay
  game=myGame(gameplay)
  run()
