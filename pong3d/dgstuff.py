# -*- coding: utf-8 -*-
"""
Fancy directgui wrapper.
It contains helper classes to speed up the making of menus and other visual stuff like that.

@author: fabius
@copyright: fabius@2010
@license: GCTA give credit to (the) authors
@version: 0.1
@date: 2010-09
@contact: astelix (U{panda3d forums<http://www.panda3d.org/forums/profile.php?mode=viewprofile&u=752>})
@status: eternal WIP

@note: see the __main__ section for a sample usage and read comments to understand how it works.

Post your dubts and inquiries in U{this forum thread<http://www.panda3d.org/phpbb2/viewtopic.php?p=56992>}

"""
import random
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject

#=========================================================================
#
class dgstuff(DirectObject):
  _DEBUG=False
  def __init__(self, data):
    self.defaultdata={}
    #
    self._setdefaultdata()
    #**
    # default data merge w/ custom data and pour back to the source
    self.data=data
    self.defaultdata.update(self.data)
    self.data.update(self.defaultdata)
    self._postdatamerge()
    self._buildcanvas()
    self.play()
  #-----------------------------------------------------
  #
  def play(self): pass
  def pause(self): pass
  def _buildcanvas(self): pass
  def _postdatamerge(self): pass
  def _setdefaultdata(self): pass
  #-----------------------------------------------------
  #
  def dbgprint(self, msg):
    if self._DEBUG: print msg
  #---------------------------------------------------
  #
  def settexture(self, model, texture=None, wrapmode='clamp', scale=None):
    """ Apply a texture over the menu panel model and set transparency automatically
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
class dgscroll(dgstuff):
  """ An helper class to ease to make a scroller panel
  """
  #-----------------------------------------------------
  #
  def _buildcanvas(self):
    # geometry setup - it is just a plane we stretch or shrink depending on the scale param - will be then applied a texture passed by data interface
    geometry=loader.loadModel('data/models/menubg.egg')
    self.settexture(geometry, self.data['texture'])
    geomscale=(self.data['scale'][0], 0, self.data['scale'][1])
    geometry.setScale(geomscale)
    b=geometry.getTightBounds()
    w,n,h=b[1]-b[0]
    #**
    # making the scrolledlist control
    self.canvas = DirectScrolledList(
      geom=geometry,
      geom_scale=geomscale,
      pos=(self.data['pos'][0], -1, self.data['pos'][1]),
      frameColor = (0, 0, 0, 0),
      itemFrame_pos = (
        -(w/2)+self.data['margin'][0], 0,
        (h/2)-self.data['margin'][1]-self.data['titlescale']-.02-self.data['itemsscale']
      ),
      numItemsVisible = self.data['itemsvisible'],
      #
      text = self.data['title'], text_scale=self.data['titlescale'],
      text_align = TextNode.ACenter,
      text_pos = (0, (h/2)-self.data['margin'][1]),
      text_fg = self.data["titlecolor"], text_font = self.data['textfont'],
      # inc and dec buttons aren't used but looks like we can't get rid easily so we put them where not visible
      decButton_pos= (-1000, 0, -1000),
      incButton_pos= (-1000, 0, -1000),
    )
    if not self.data['visible']: self.canvas.hide()
    #
    self._additems(w, h)
    #
    self.index=self.data['selected']
    self._hilightcurrent(True)
  #-----------------------------------------------------
  #
  def _setdefaultdata(self):
    self.defaultdata={
      'scale':(.6,.75), 'margin':(.15,.15), 'itemsvisible':10,
      'texture':None, 'pos':(0,0), 'title':'* TITLE *',
      'titlescale':.07, 'titlecolor':(0,0,0,1), 'highlightcolor':(1,1,0,1),
      'textfont':loader.loadFont("cmss12.egg"), 'itemsscale':.05,
      'items':[], 'itemscolor':(0,0,0,1), 'roundrobin':False,
      'callback':None, 'selected':0, 'visible':True, 'exit':None,
    }
  #-----------------------------------------------------
  #
  def _postdatamerge(self):
    self.defaultcallback=self.data["callback"] or self.onClick
    self.roundrobin=self.data["roundrobin"]
    self.highlight=self.data["highlightcolor"]
  #-----------------------------------------------------
  #
  def _additems(self): pass
  #-----------------------------------------------------
  #
  def play(self):
    """ (re)start the menu controls """
    self.accept("wheel_up", self.scrollindex, [-1] )
    self.accept("wheel_down", self.scrollindex, [1] )
    self.accept("arrow_up", self.scrollindex, [-1] )
    self.accept("arrow_down", self.scrollindex, [1] )
    self.accept("enter", self._click)
    if callable(self.data['exit']): self.accept("escape", self.data['exit'])
    for item in self.canvas["items"]: item['state']=DGG.NORMAL
  #-----------------------------------------------------
  #
  def pause(self):
    """ pause the menu controls """
    for item in self.canvas["items"]: item['state']=DGG.DISABLED
    self.ignoreAll()
  #-----------------------------------------------------
  #
  def finish(self):
    self.ignoreAll()
    self.canvas.destroy()
  #-----------------------------------------------------
  #
  def _click(self):
    """ called when click over an item is routed (i.e. via keyboard) """
    if hasattr(self.canvas["items"][self.index], 'commandFunc'):
      self.canvas["items"][self.index].commandFunc(None)
  #-----------------------------------------------------
  #
  def onClick(self, *value):
    """ Common callback for all the items with no specific callback defined (to be overriden)
    """
    self.dbgprint("[CLASS CB]item clicked w/ value: %r"%(value))
  #-----------------------------------------------------
  #
  def butenex(self, evt, index, pos):
    """ Hilight management entering and exiting w/ the mouse pointer """
    if evt == DGG.ENTER:
      self._hilightcurrent(False)
      self.index=index
      self._hilightcurrent(True)
    elif evt == DGG.EXIT:
      self._hilightcurrent(False)
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
    """ Set the actually selected item highlight on or off """
    if len(self.canvas["items"]):
      self.canvas["items"][self.index]['frameColor']=\
        list(self.highlight)[:3]+[self.highlight[3] if onoff else 0]

#=========================================================================
#
class dgmenu(dgscroll):
  #-----------------------------------------------------
  #
  def _additems(self, w,h):
    """ Add items as buttons to the scrolling panel.
    @note: color, textscale and font could be either assigned overall or per item
    """
    for idx in range(len(self.data['items'])):
      default={
        'color': self.data['itemscolor'],
        'textscale': self.data['itemsscale'],
        'textfont': self.data['textfont'],
        'width': w-(self.data['margin'][0]*2.),
      }
      self.data['items'][idx].update(default)
      self.addItem(idx, **self.data['items'][idx])

  #-----------------------------------------------------
  #
  def addItem(self, index, **keys):
    """ An item is a clickable label that fires a callback.

    There are 2 possible scenarios:
     - 1 common callback for all (onClick) overridable (defined in the main data, see __init__)
     - 1 custom callback carried on the item via 'callback' data element
     for each of them will be passed the item index in the list
     @note: textfont is mandatorily passed by the caller
    """
    itemdata={
      'label':'label_%d'%index, 'width':.4, 'textscale':.05,
      'color':(0,0,0,1), 'callback':self.defaultcallback,
    }
    # default data merge w/ custom params  passed to the method
    itemdata.update(keys)
    #
    w,h=(itemdata['width'], itemdata['textscale'])
    butt = DirectButton(
      text = tuple([itemdata['label']]*4), text_fg=itemdata['color'],
      text_scale=itemdata['textscale'], text_align=TextNode.ALeft,
      text_font=itemdata['textfont'],
      relief=2, borderWidth = (0.0, 0.0),
      frameSize = (0.0, w, (-h/2.)+.02, (h/2.)+.01),  frameColor=(0,0,0,0),
      command=itemdata['callback'], extraArgs=[index],
    )
    #
    butt.bind(DGG.ENTER, self.butenex, [DGG.ENTER, index])
    butt.bind(DGG.EXIT, self.butenex, [DGG.EXIT, index])
    self.canvas.addItem(butt, True)

#=========================================================================
#
class dgtable(dgscroll):
  """ Helper class to ease making of a scrolling table og columnar data.
  """
  #-----------------------------------------------------
  #
  def _setdefaultdata(self):
    dgscroll._setdefaultdata(self)
    # data interface at instancing - you define just the parameters you need to customize
    self.defaultdata.update({'head':[], 'exit': None})
  #-----------------------------------------------------
  #
  def _postdatamerge(self):
    # skip if there are no items
    if not len(self.data['items']): return
    dgscroll._postdatamerge(self)
    # calculate the column width, where not explicitly specified, subdividing the space per columns
    self.data['itemswidth']=self.data.get(
      'itemswidth',
      [
        self.data['scale'][1] / len(self.data['items'])
      ]*len(self.data['items'])
    )
  #-----------------------------------------------------
  #
  def _additems(self, w, h):
    # add the column heading
    for icol in range(len(self.data['head'])):
      idata={
        'color': self.data['itemscolor'],
        'textfont': self.data['textfont'],
        'textscale': self.data['itemsscale'],
      }
      self.data['head'][icol]['width']=self.data['itemswidth'][icol]
      idata.update(self.data['head'][icol])
      self.data['head'][icol]=idata
    self.addHead(self.data['head'], -(w/2)+self.data['margin'][0],
      (h/2)-self.data['margin'][1]-self.data['titlescale']-.02
    )
    """ add items as buttons
    NOTE color, textscale and font could be either assigned overall or per item
    """
    for idx in range(len(self.data['items'])):
      for icol in range(len(self.data['items'][idx])):
        idata={
          'color': self.data['itemscolor'],
          'textfont': self.data['textfont'],
          'textscale': self.data['itemsscale'],
        }
        idata.update(self.data['items'][idx][icol])
        self.data['items'][idx][icol]=idata
        self.data['items'][idx][icol]['width']=self.data['itemswidth'][icol]

      self.addRow(idx, self.data['items'][idx])
  #-----------------------------------------------------
  #
  def addRow(self, index, rowdata):
    """
    """
    w0=0.0
    h0=0.0
    l=[]
    for col in rowdata:
      itemdata={
        'label':'label_%d'%index, 'width':.4, 'textscale':.05,
        'color':(0,0,0,1),
      }
      # default data merge w/ custom params  passed to the method
      itemdata.update(col)
      #
      w,h=(itemdata['width'], itemdata['textscale'])
      butt = DirectButton(
        text = itemdata['label'], text_fg=itemdata['color'],
        text_scale=itemdata['textscale'], text_align=TextNode.ALeft,
        text_font=itemdata['textfont'],
        text_pos=(w0,0.01),
        relief=2, borderWidth = (0.0, 0.0),
        frameSize = (w0, w0+w, (-h/2.)+.03, (h/2.)+.03),  frameColor=(1,0,0,0),
      )
      butt.bind(DGG.ENTER, self.butenex, [DGG.ENTER, index])
      butt.bind(DGG.EXIT, self.butenex, [DGG.EXIT, index])
      l.append(butt)
      w0+=w
      h0=max(h0,h)
    row=DirectFrame(
      frameColor=(0,0,0,0) , frameSize=(0,w0,0,h),
    )
    # NOTE trick to attach a callback to the frame as it was a button (click via kbd)
    row.commandFunc=lambda foo=None: self.defaultcallback(index)
    for c in l: c.reparentTo(row)
    self.canvas.addItem(row, True)
  #-----------------------------------------------------
  #
  def addHead(self, rowdata, w0, h0):
    """
    """
    l=[]
    i=0
    for col in rowdata:
      itemdata={
        'label':'COL_%d'%i, 'width':.4, 'textscale':.05, 'color':(0,0,0,1),
      }
      i+=1
      # default data merge w/ custom params  passed to the method
      itemdata.update(col)
      #
      w,h=(itemdata['width'], itemdata['textscale'])
      butt = DirectLabel(
        text = itemdata['label'], text_fg=itemdata['color'],
        text_scale=itemdata['textscale'], text_align=TextNode.ALeft,
        text_font=itemdata['textfont'],
        text_pos=(w0,0.01),
        relief=2, borderWidth = (0.0, 0.0),
        frameSize = (w0, w0+w, (-h/2.)+.03, (h/2.)+.03),  frameColor=(1,0,0,0),
      )
      l.append(butt)
      w0+=w
    #
    row=DirectFrame(
      frameColor=(0,0,0,0) , frameSize=(0,w0,0,h),
    )
    for c in l: c.reparentTo(row)
    row.setZ(h0)
    row.reparentTo(self.canvas)
#=========================================================================
#
class dginput(dgstuff):
  """
  @todo: aggiungere callback principale (si attiva ALLA CONFERMA dell'input)
  """
  #-----------------------------------------------------
  #
  def _setdefaultdata(self):
    # overridiamo completamente
    self.defaultdata={
      'bgcolor': (1,1,1,0), 'texture': None, 'margin':(0.,0.),
      'title': "** TITLE **", 'titlescale': .08,
      'align': 'left', 'textfont':loader.loadFont("cmss12.egg"),
      'pos':(0,0), 'scale': (.6, .1), 'titlecolor':(0,0,0,1),
      'inputwidth':10, 'inputscale': .07, 'initialtext': '', 'focus': 0,
      'inputcolor':(0,0,0,1), 'autoexit': False,
    }
  #-----------------------------------------------------
  #
  def _buildcanvas(self):
    w,h=self.data['scale']
    geometry=geomscale=None
    if self.data['texture']:
      geometry=loader.loadModel('data/models/menubg.egg')
      self.settexture(geometry, self.data['texture'])
      geomscale=(
        self.data['scale'][0]+self.data['margin'][0], 0,
        self.data['scale'][1]+self.data['margin'][1]
      )
    #
    # by default titlepos is to the entry control left, but you can optionally set it to the top so the entry will be put to the frame center
    self.data['align']=self.data['align'].lower()
    if self.data['align'] == 'center':
      textpos=(0, (h/2)-self.data['margin'][1])
      textalign=TextNode.ACenter
    else:
      textpos=(-(w/2.)+self.data['margin'][0],0)
      textalign=TextNode.ALeft
    #
    self.canvas = DirectFrame(
      geom=geometry,
      geom_scale=geomscale,
      pos=(self.data['pos'][0],0,self.data['pos'][1]),
      frameSize=(-w/2.,w/2.,-h/2.,h/2), frameColor=self.data['bgcolor'],
      text = self.data['title'], text_align = textalign,
      text_pos = textpos, text_font = self.data['textfont'],
      text_fg=self.data['titlecolor'], text_scale=self.data['titlescale'],
    )
    self.entry = DirectEntry(
      parent=self.canvas, pos=(0,0,0), frameColor=(1,1,1,0),
      text_font = self.data['textfont'],  text_fg=self.data['inputcolor'],
      text_scale=self.data['inputscale'],
      initialText=self.data['initialtext'], numLines=1,
      width=self.data['inputwidth']/2., focus=self.data['focus'],
      command=self._settext, focusInCommand=self._cleartext,
    )
    if self.data['align'] == 'center':
      b=self.entry.getBounds()
      w=b[1]
      self.entry.setPos(-(w/2.)+self.data['margin'][0],0,0)
  #-----------------------------------------------------
  #
  def _settext(self, textEntered):
    """ Callback function entering text to the control """
    if textEntered.strip() == '':
      textEntered=self.data['initialtext']
      self.entry.enterText(textEntered)
    else:
      if callable(self.data['callback']): self.data['callback'](textEntered)
      if self.data['autoexit'] and callable(self.data['exit']):
        # NOTE not safe to call here user callback...
        taskMgr.doMethodLater(.5, self.data['exit'], '_ntryxt')
  #-----------------------------------------------------
  #
  def _cleartext(self):
    text=self.entry.get(plain=True).strip()
    if text == self.data['initialtext']: self.entry.enterText('')
    else: self.entry.setCursorPosition(len(text))
  #-----------------------------------------------------
  #
  def play(self):
    """ (re)start the control
    @note: SetFocus actually won't work
    """
    def focusentry(): self.entry['focus']=True
    self.accept("tab", focusentry)
    if callable(self.data['exit']): self.accept("escape", self.data['exit'])
    self.entry['state']=DGG.NORMAL
  #-----------------------------------------------------
  #
  def pause(self):
    """ pause the menu controls """
    self.entry['state']=DGG.DISABLED
    self.ignoreAll()
  #-----------------------------------------------------
  #
  def finish(self):
    self.ignoreAll()
    self.entry.destroy()
    self.canvas.destroy()

#=========================================================================
#
if __name__ == "__main__":
  """ dgscrollers sample usage """
  import direct.directbase.DirectStart
  import sys

  # Some gui stuff
  title="Fancy DirectGUI"
  content="Use of gui stuff to ease to make menus, tables\nand inputs using a compact data interface"
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

  env=loader.loadModel("environment")
  env.reparentTo(render)

  #** handler called by menu_options_video
  def setvideo(index=None):
    global menu_options_video
    def _setresolution(res, fullscreen=False):
        wp = WindowProperties()
        wp.setSize(int(res[0]), int(res[1]))
        wp.setFullscreen(fullscreen)
        base.win.requestProperties(wp)
    if index <> None:
      video=menu_options_video['items'][index]['label']
      infotext['message'].setText("Video changed to %r"%video)
      _setresolution(video.split('x'))

  menulist=[]
  #** used for the menu ovelapping mechanic to add a menu over
  def push_menu(menudata):
    global menulist
    if len(menulist): menulist[-1].pause()
    menulist.append(dgmenu(menudata))

  #** used for the menu ovelapping mechanic to add a menu over
  def push_table(menudata):
    global menulist
    if len(menulist): menulist[-1].pause()
    menulist.append(dgtable(menudata))

  #** used for the menu ovelapping mechanic to add a menu over
  def push_entry(menudata):
    global menulist
    if len(menulist): menulist[-1].pause()
    menulist.append(dginput(menudata))

  #** used for the menu ovelapping mechanic to close the overall menu
  def pop_menu(foo=None):
    global menulist
    menu=menulist.pop()
    menu.finish()
    if len(menulist): menulist[-1].play()

  def exit(foo=None):
    self.dbgprint("quitting out...")
    sys.exit(0)

  menu_options_video={'title': 'Video Options',
    'scale':(.4, .6), 'itemsvisible':10, 'titlescale':.05,
    'texture':'data/models/textures/iphone.png', 'margin':(.12, .34),
    'callback': setvideo,
    'items': [
      {'label': '800x600'},
      {'label': '1024x768'},
      {'label': 'back', 'callback': pop_menu, },
    ],
    'exit': pop_menu,
  }

  menu_options={'title': 'Options',
    'scale':(.4, .6), 'itemsvisible':10, 'titlescale':.05,
    'texture':'data/models/textures/iphone.png', 'margin':(.12, .34),
    'callback': None,
    'items': [
      {'label': 'video',
        'callback': lambda foo=None: push_menu(menu_options_video),
      },
      {'label': 'opponent', 'callback':None, 'choice': 1},
      {'label': 'back', 'callback': pop_menu, },
    ],
    'exit': pop_menu,
  }
  menu_quitgame={'title': 'Sure to quit "game"?',
    'scale':(.46, .34), 'itemsvisible':6, 'margin':(.25, .2),
    'texture':'data/models/textures/round256x128.png', 'selected': 1,
    'items': [
      {'label': 'Yes', 'width': .1, 'callback': exit},
      {'label': 'No', 'width': .1, 'callback': pop_menu, },
    ],
    'itemselected': 1, 'exit': pop_menu,
  }
  #**
  def prot(foo=None): self.dbgprint(foo)
  table0={'title': 'TOP 10', 'titlescale': .08,
    'scale':(.62, .44), 'itemsvisible':6, 'pos':(-.5, .1), 'margin': (.25,.23),
    'texture':'data/models/textures/menubg01.png',
    'itemswidth': (.45,.15,.15),
    'items': [
      [ {'label': 'Row0Col0',}, {'label': 'R0C1',}, {'label': 'R0C2',}, ],
      [ {'label': 'Row1Col0',}, {'label': 'R1C1',}, {'label': 'R1C2',}, ],
      [ {'label': 'Row2Col0',}, {'label': 'R2C1',}, {'label': 'R2C2',}, ],
      [ {'label': 'Row3Col0',}, {'label': 'R3C1',}, {'label': 'R3C2',}, ],
      [ {'label': 'Row4Col0',}, {'label': 'R4C1',}, {'label': 'R4C2',}, ],
      [ {'label': 'Row5Col0',}, {'label': 'R5C1',}, {'label': 'R5C2',}, ],
      [ {'label': 'Row6Col0',}, {'label': 'R6C1',}, {'label': 'R6C2',}, ],
      [ {'label': 'Row7Col0',}, {'label': 'R7C1',}, {'label': 'R7C2',}, ],
      [ {'label': 'Row8Col0',}, {'label': 'R8C1',}, {'label': 'R8C2',}, ],
      [ {'label': 'Row9Col0',}, {'label': 'R9C1',}, {'label': 'R9C2',}, ],
    ],
    'head': [
      { 'label': 'COL0'},
      { 'label': 'COL1'},
      { 'label': 'COL2'},
    ],
    'callback': prot, 'exit': pop_menu
  }
  #**
  def printv(v): infotext['message'].setText("Player Name: '%s'"%v)
  entry0={
    'xpos': (-.5,.0), 'align': 'center',
    'title': 'Player Name', 'scale': (1.2,.6), 'margin':(.07, .05),
    'titlecolor': (0,0,1,1), 'texture':'data/models/textures/round256x128.png',
    'initialtext': "Type Something", 'inputscale': .07, 'inputwidth': 25,
    'inputcolor':(0,1,0,1),
    'callback': lambda v: printv(v), 'exit': pop_menu, 'autoexit': True,
  }
  #**
  menu_main={'title': 'MAIN MENU', 'titlescale': .08,
    'scale':(.62, .6), 'itemsvisible':14, 'pos':(-.8, .2), 'margin': (.25,.23),
    'texture':'data/models/textures/menubg01.png', 'itemsscale': .07,
    'items': [
      {'label': 'Options',
        'callback': lambda foo=None: push_menu(menu_options),
      },
      {'label': 'TOP10',
        'callback': lambda foo=None: push_table(table0),
      },
      {'label': 'New Game',
        'callback': lambda foo=None: push_entry(entry0),
      },
      {'label': 'Exit', 'callback': lambda foo=None: push_menu(menu_quitgame),
      },
    ],
    'exit': lambda foo=None: push_menu(menu_quitgame),
  }

  push_menu(menu_main)

  run()
