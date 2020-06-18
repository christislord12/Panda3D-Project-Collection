# -*- coding: utf-8 -*-
"""
Fancy menus using DirectScrolledList
by: fabius astelix @ 2010-04-29
see the __main__ section for a sample usage and read comments to understand how it works.
Post your dubts and inquiries in this forum thread: http://www.panda3d.org/phpbb2/viewtopic.php?p=56992
"""
import random
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from direct.directbase import DirectStart

#=========================================================================
#
class dgmenu(DirectObject):
  QUITVALUE="_quit_"
  #-----------------------------------------------------
  #
  def __init__(self, data):
    """
    NOTE
      - data sizes and positions have just the xz components
      - items are automatically added to the list defining an items list of dictionary data (see addItem method for info)
    """
    self.data=data
    # data interface at instancing - you define just the parameters you need to customize
    defaultdata={
        'scale':(.6, .75), 'margin':(.25, .25), 'itemsvisible':14,
        'texture':None, 'pos':(0,0), 'title': '* MENU TITLE *',
        'titlescale':.07, 'titlecolor':(0,0,0,1), 'highlightcolor':(1,1,0,1),
        'items':[], 'itemscolor':(0,0,0,1), 'roundrobin':False,
        'callback':None, 'selected': 0,
    }
    # default data merge w/ custom data and pur back to the source
    defaultdata.update(self.data)
    self.data.update(defaultdata)
    #
    self.defaultcallback=data["callback"] or self.onClick
    self.roundrobin=data["roundrobin"]
    self.highlight=data["highlightcolor"]
    # menu geometry - it is just a plane we stretch or shrink depending on the scale param - will be then applied a texture passed by data interface
    geometry=loader.loadModel('data/models/menubg.egg')
    self.settexture(geometry, data['texture'])
    geometry.setScale(data['scale'][0], 0, data['scale'][1])
    b=geometry.getTightBounds()
    w,n,h=b[1]-b[0]
    #
    self.canvas = DirectScrolledList(
      geom=geometry,
      geom_scale=(data['scale'][0], 0, data['scale'][1]),
      pos=(data['pos'][0], -1, data['pos'][1]),
      frameColor = (0, 0, 0, 0),
      itemFrame_pos = (
        -(w/2)+data['margin'][0], 0, (h/2)-data['margin'][1]-data['titlescale']
      ),
      numItemsVisible = data['itemsvisible'],
      #
      text = data['title'], text_scale=data['titlescale'],
      text_align = TextNode.ACenter, text_pos = (0, (h/2-data['margin'][1])),
      text_fg = data["titlecolor"],
      # inc and dec buttons aren't used but looks like we can't get rid easily so we put them where not visible
      decButton_pos= (-1000, 0, -1000),
      incButton_pos= (-1000, 0, -1000),
    )
    """ adding the items (as buttons)
    NOTE 'color' member of items list override the overall 'itemscolor'
    """
    for idx in range(len(data['items'])):
      data['items'][idx]['color']=data['items'][idx].get(
        'color', data['itemscolor']
      )
      self.addItem(idx, **data['items'][idx])
    #
    self.index=self.data['selected']
    self._hilightcurrent(True)
    self.play()

  #-----------------------------------------------------
  #
  def play(self):
    self.accept("wheel_up", self.scrollindex, [-1] )
    self.accept("wheel_down", self.scrollindex, [1] )
    self.accept("arrow_up", self.scrollindex, [-1] )
    self.accept("arrow_down", self.scrollindex, [1] )
    self.accept("enter", self._click)
    for item in self.canvas["items"]:
      if item._backitem: self.accept("escape", item.commandFunc, [None])

  #-----------------------------------------------------
  #
  def pause(self): self.ignoreAll()

  #-----------------------------------------------------
  #
  def finish(self):
    self.ignoreAll()
    self.canvas.destroy()

  #-----------------------------------------------------
  #
  def _click(self):
    """ called when click over an item is routed (i.e. via keyboard)
    """
    if hasattr(self.canvas["items"][self.index], 'commandFunc'):
      self.canvas["items"][self.index].commandFunc(None)

  #-----------------------------------------------------
  #
  def onClick(self, *value):
    """ common callback for all the items with no specific callback defined - to be overriden by
    """
    print "[CLASS CB]item clicked w/ value: %r"%(value)

  #-----------------------------------------------------
  #
  def scrollindex(self, delta):
    self._hilightcurrent(False)
    i=self.index+delta
    if self.roundrobin: self.index=i%len(self.canvas["items"])
    else: self.index=max(0, min(i, len(self.canvas["items"])-1))
    self._hilightcurrent(True)
    self.canvas.scrollTo(self.index, True)

  #-----------------------------------------------------
  #
  def _hilightcurrent(self, onoff):
    """ set the highlight of the actually selected item on or off
    """
    if len(self.canvas["items"]):
      self.canvas["items"][self.index]['frameColor']=\
        list(self.highlight)[:3]+[self.highlight[3] if onoff else 0]

  #-----------------------------------------------------
  #
  def addItem(self, index, **keys):
    """ an item is a clickable label that fires a callback.
    There are 2 possible scenarios:
     - 1 common callback for all (onClick) overridable (defined in the main data - see __init__)
     - 1 custom callback carried on the item via 'value' data element
     for each of them will be passed the 'value' by default or the label if the value is undefined or the whole item data (self.data) if 'value' is a callback
    """
    itemdata={
      'label':'label_%d'%index, 'width':.4, 'textscale':.05,
      'color':(0,0,0,1), 'value':None, 'back': False
    }
    # default data merge w/ custom params  passed to the method
    itemdata.update(keys)
    #
    if callable(itemdata['value']):
      callback=itemdata['value']
      itemdata['value']=self.data
    elif itemdata['value'] == self.QUITVALUE: callback=self.finish
    else: callback=self.defaultcallback
    # if value is unspecified will be then applied the label as a value
    if itemdata['value'] == None: itemdata['value']=itemdata['label']
    w,h=(itemdata['width'], itemdata['textscale'])
    butt = DirectButton(
      text = tuple([itemdata['label']]*4), text_fg=itemdata['color'],
      text_scale=itemdata['textscale'], text_align=TextNode.ALeft,
      borderWidth = (0.0, 0.0), relief=2,
      frameSize = (0.0, w, (-h/2.)+.01, (h/2.)+.01),  frameColor=(0,0,0,0),
      command=callback, extraArgs=[itemdata['value']],
    )
    #
    butt.bind(DGG.ENTER, self.butenex, [DGG.ENTER, index])
    butt.bind(DGG.EXIT, self.butenex, [DGG.EXIT, index])
    # if true means ESCAPE key must call this item's callback
    butt._backitem=itemdata['back']
    self.canvas.addItem(butt, True)

  #-----------------------------------------------------
  #
  def butenex(self, evt, index, pos):
    """ hilight management entering and exiting w/ the mouse pointer """
    if evt == DGG.ENTER:
      self._hilightcurrent(False)
      self.index=index
      self._hilightcurrent(True)
    elif evt == DGG.EXIT:
      self._hilightcurrent(False)

  #---------------------------------------------------
  #
  def settexture(self, model, texture=None, wrapmode='clamp', scale=None):
    """ apply a texture over the menu panel model and set transparency automatically
    """
    wraps={'repeat': Texture.WMRepeat, 'clamp': Texture.WMClamp,}
    if texture:
      tex = loader.loadTexture(texture)
      model.clearTexture()
      tex.setWrapU(wraps[wrapmode])
      tex.setWrapV(wraps[wrapmode])
      tex.setMinfilter(Texture.FTLinearMipmapNearest)
      ts = TextureStage('ts')
      model.setTexture(ts, tex, 1)
      if scale: model.setTexScale(ts, scale[0], scale[1])
      # autotransparent if png image file
      if texture.endswith('.png'):
        model.setTransparency(TransparencyAttrib.MAlpha)

#=========================================================================
#
if __name__ == "__main__":
  import sys
  """ dgmenu sample usage
  """
  env=loader.loadModel("environment")
  env.reparentTo(render)

  #** handler called by menu_options_video
  def setvideo(video=None):
    def _setresolution(res, fullscreen=False):
        wp = WindowProperties()
        wp.setSize(int(res[0]), int(res[1]))
        wp.setFullscreen(fullscreen)
        base.win.requestProperties(wp)
    if video <> None:
      infotext['message'].setText("Video changed to %r"%video)
      _setresolution(video.split('x'))

  menulist=[]
  def push_menu(menudata):
    """ used for the menu ovelapping mechanic to add a menu over
    """
    global menulist
    if len(menulist): menulist[-1].pause()
    menulist.append(dgmenu(menudata))

  def pop_menu(foo=None):
    """ used for the menu ovelapping mechanic to close the overall menu
    """
    global menulist
    menu=menulist.pop()
    menu.finish()
    if len(menulist): menulist[-1].play()

  def exit(foo=None):
    print "quitting out..."
    sys.exit(0)

  menu_options_video={'title': 'Video Options',
    'scale':(.40, .6), 'itemsvisible':10, 'titlescale':.05,
    'texture':'data/models/textures/iphone.png', 'margin':(.12, .34),
    'callback': setvideo,
    'items': [
      {'label': '800x600'},
      {'label': '1024x768'},
      {'label': 'back', 'value': pop_menu, 'back': True},
    ],
  }

  menu_options={'title': 'Options',
    'scale':(.40, .6), 'itemsvisible':10, 'titlescale':.05,
    'texture':'data/models/textures/iphone.png', 'margin':(.12, .34),
    'callback': None,
    'items': [
      {'label': 'video',
        'value': lambda foo=None: push_menu(menu_options_video),
      },
      {'label': 'opponent', 'value': ['Human', 'CPU'], 'choice': 1},
      {'label': 'back', 'value': pop_menu, 'back': True},
    ],
  }
  menu_quitgame={'title': 'Sure to quit <game>?',
    'scale':(.46, .34), 'itemsvisible':6, 'margin':(.25, .2),
    'texture':'data/models/textures/round256x128.png', 'selected': 1,
    'items': [
      {'label': 'Yes', 'width': .1, 'value': exit},
      {'label': 'No', 'width': .1, 'value': pop_menu, 'back': True},
    ], 'itemselected': 1
  }
  menu_main={'title': 'MAIN MENU',
    'scale':(.62, .6), 'itemsvisible':14, 'pos':(-.8, .2),
    'texture':'data/models/textures/menubg01.png',
    'items': [
      {'label': 'Options',
        'value': lambda foo=None: push_menu(menu_options),
      },
      {'label': 'Exit', 'back': True,
        'value': lambda foo=None: push_menu(menu_quitgame),
      },
    ],
  }

  push_menu(menu_main)

  # Some gui stuff
  title="Fancy Menus"
  content=""""Use of DirectScrolledList to ease to make menus using a compact
data interface"""
  infotext={}
  infotext['title']=OnscreenText(
    text = title, pos = (0, .92), scale = 0.08, mayChange=True, fg=(1,1,1,1),
    bg=(0,0,1,.7)
  )
  infotext['content']=OnscreenText(
    text = content, pos = (0, 0.84), scale = 0.05, mayChange=True, fg=(1,1,0,1),
    bg=(0,0,0,.5)
  )
  infotext['message']=OnscreenText(
    text = '', pos = (0, -0.85), scale = 0.07, mayChange=True, fg=(1,1,1,1),
    bg=(1,0,0,.65)
  )

  run()
