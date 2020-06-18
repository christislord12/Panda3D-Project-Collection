#!/bin/env python
'''
by: Fabius @  200902 loosely based on Robin Dunn's wx demo code

A custom multi-purposes editor using the stc.StyledTextCtrl component
'''
import  keyword
import  os, wx
import  wx.stc  as  stc
import  wxutils as wxut
#=======================================================================
#
class customSTC(stc.StyledTextCtrl):
  lexers={
    'AUTO': wx.stc.STC_LEX_AUTOMATIC,
    'BASH':wx.stc.STC_LEX_BASH,
    'CSS':wx.stc.STC_LEX_CSS,
    'HTML':wx.stc.STC_LEX_HTML,
    'MAKE':wx.stc.STC_LEX_MAKEFILE,
    'PERL':wx.stc.STC_LEX_PERL,
    'PHP':wx.stc.STC_LEX_PHPSCRIPT,
    'PYTHON':wx.stc.STC_LEX_PYTHON,
    'SQL':wx.stc.STC_LEX_SQL,
    'XML':wx.stc.STC_LEX_XML,
  }
  #------------------------------------------------------------------
  #
  def __init__(self, parent, ID=-1,
    pos=wx.DefaultPosition, size=wx.DefaultSize,
    style=0, lexer='AUTO'
  ):
    stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

    self.CmdKeyAssign(ord('+'), stc.STC_SCMOD_ALT, stc.STC_CMD_ZOOMIN)
    self.CmdKeyAssign(ord('-'), stc.STC_SCMOD_ALT, stc.STC_CMD_ZOOMOUT)

    self.changeLexer(lexer)

    self.SetKeyWords(0, " ".join(keyword.kwlist))

    self.SetProperty("fold", "0")
    self.SetProperty("tab.timmy.whinge.level", "1")
    self.SetViewWhiteSpace(False)
    self.SetWrapMode(stc.STC_WRAP_WORD)
    #self.SetBufferedDraw(False)
    #self.SetViewEOL(True)
    #self.SetEOLMode(stc.STC_EOL_CRLF)
    #
    self.SetMargins(2,2)
    self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
    self.SetMarginWidth(1, 32)
    # Proscribed indent size for wx
    tabsz=2
    self.SetIndent(tabsz)
    self.SetIndentationGuides(True)
    self.SetBackSpaceUnIndents(True)
    self.SetTabIndents(True)
    self.SetTabWidth(tabsz)
    # Use spaces rather than tabs
    self.SetUseTabs(False)
    # Global default style
    if wx.Platform == '__WXMSW__':
      self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
        'fore:#000000,back:#FFFFFF,face:Courier New,size:9'
      )
    elif wx.Platform == '__WXMAC__':
      self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
        'fore:#000000,back:#FFFFFF,face:Monaco'
    )
    else:
      self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
        'fore:#000000,back:#FFFFFF,face:Monospace,size:9'
      )
    # Clear styles and revert to default.
    self.StyleClearAll()
    #common styles
    styles=[
      (wx.stc.STC_STYLE_LINENUMBER,'fore:#000000,back:#99A9C2'),
      (wx.stc.STC_STYLE_BRACELIGHT,'fore:#00009D,back:#FFFF00'),
      (wx.stc.STC_STYLE_BRACEBAD,'fore:#00009D,back:#FF0000'),
      (wx.stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD"),
    ]
    for style in styles: self.StyleSetSpec(*style)
    # Python styles
    styles=[
      (wx.stc.STC_P_DEFAULT, 'fore:#000000'),
      (wx.stc.STC_P_COMMENTLINE,  'fore:#008000,back:#F0FFF0'),
      (wx.stc.STC_P_COMMENTBLOCK, 'fore:#008000,back:#F0FFF0'),
      (wx.stc.STC_P_NUMBER, 'fore:#008080'),
      (wx.stc.STC_P_STRING, 'fore:#800080'),
      (wx.stc.STC_P_CHARACTER, 'fore:#800080'),
      (wx.stc.STC_P_WORD, 'fore:#000080,bold'),
      (wx.stc.STC_P_TRIPLE, 'fore:#800080,back:#FFFFEA'),
      (wx.stc.STC_P_TRIPLEDOUBLE, 'fore:#800080,back:#FFFFEA'),
      (wx.stc.STC_P_CLASSNAME, 'fore:#0000FF,bold'),
      (wx.stc.STC_P_DEFNAME, 'fore:#008080,bold'),
      (wx.stc.STC_P_OPERATOR, 'fore:#800000,bold'),
      (wx.stc.STC_P_IDENTIFIER, 'fore:#000000'),
    ]
    for style in styles: self.StyleSetSpec(*style)
    #
    self.SetCaretForeground("BLUE")
    self.SetSelBackground(True,
      wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
    )
    self.SetSelForeground(True,
      wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
    )
    #
    ###self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
    self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
    self.Bind(stc.EVT_STC_START_DRAG, self.OnStartDrag)
  #------------------------------------------------------------------
  #
  def OnStartDrag(self, event):
    # this will disable the actual buggy internal dnd feature
    event.SetDragText('')
    event.Skip()
  #------------------------------------------------------------------
  #
  def processKey(self, evt):
    keycode = 0
    key = evt.KeyCode
    if "unicode" in wx.PlatformInfo:
      keycode = evt.GetUnicodeKey()
      if keycode <= 127: keycode = evt.GetKeyCode()
      readchar=unichr(keycode)
    elif keycode in range(1,256):
      keycode = evt.GetKeyCode()
      readchar=chr(keycode)
    else: readchar="?"
    return (keycode, readchar)
  #------------------------------------------------------------------
  #
  def changeLexer(self, lexer):
    try:
      self.SetLexer(self.lexers[lexer.upper()])
    except:
      self.SetLexer(self.lexers['AUTO'])
  #------------------------------------------------------------------
  #
  def OnUpdateUI(self, evt):
    # check for matching braces
    braceAtCaret = -1
    braceOpposite = -1
    charBefore = None
    caretPos = self.GetCurrentPos()
    if caretPos > 0:
      charBefore = self.GetCharAt(caretPos - 1)
      styleBefore = self.GetStyleAt(caretPos - 1)
    # check before
    if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
      braceAtCaret = caretPos - 1
    # check after
    if braceAtCaret < 0:
      charAfter = self.GetCharAt(caretPos)
      styleAfter = self.GetStyleAt(caretPos)
      if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
        braceAtCaret = caretPos
    if braceAtCaret >= 0:
      braceOpposite = self.BraceMatch(braceAtCaret)
    if braceAtCaret != -1  and braceOpposite == -1:
      self.BraceBadLight(braceAtCaret)
    else:
      self.BraceHighlight(braceAtCaret, braceOpposite)
#=======================================================================
#
class mupuEd(object):
  '''multi-purposes editor class
  '''
  ID_SAVEFILE=10
  ID_SAVEFILE_AS=15
  ID_OPENFILE=20
  ext2lex={
    '*': 'HTML',
    'sh,csh': 'BASH',
    'css': 'CSS',
    'txt,htm,html,php': 'HTML',
    'py': 'PYTHON',
    'xml,xlt': 'XML',
  }
  #------------------------------------------------------------------
  #
  def __init__(self, parent):
    #
    self.parent=parent
    self.nosave = False
    self._filepath=""
    #
    self.tbar=wx.ToolBar(parent,
      style=wx.TB_HORIZONTAL| wx.NO_BORDER| wx.TB_FLAT
    )
    tsize=(24,24)
    self.tbar.SetToolBitmapSize(tsize)
    ##
    self.tbar.AddLabelTool(
      self.ID_OPENFILE, "Load",
      wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize),
      shortHelp="Load file", longHelp="Load a file from disk."
    )
    ##
    self.tbar.AddLabelTool(
      self.ID_SAVEFILE, "Save",
      wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize),
      shortHelp="Save file", longHelp="Save loaded file or a new one."
    )
    self.tbar.EnableTool(self.ID_SAVEFILE, False)
    ##
    self.tbar.AddLabelTool(
      self.ID_SAVEFILE_AS, "Save As",
      wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, tsize),
      shortHelp="Save file as", longHelp="Save the file with another name."
    )
    #
    self.editor=customSTC(parent, pos=(0,30), style=wx.CLIP_CHILDREN, lexer='auto')
    self.editor.SetFocus()
    #
    self.status=wx.StatusBar(parent, style=0)
    #
    parent.Bind(wx.EVT_CLOSE, self.OnClose)
    self.tbar.Bind(wx.EVT_TOOL, self._onToolClick)
    self.editor.Bind(wx.EVT_KEY_UP, self._onKeyPressed)
    #
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self.tbar, 0, wx.EXPAND)
    sizer.Add(self.editor, 3, wx.EXPAND)
    sizer.Add(self.status, 0, wx.EXPAND)
    parent.SetSizer(sizer)
    self.status.SetStatusText("Welcome, chap!")
    #this at last
    self.tbar.Realize()
  #------------------------------------------------------------------
  #
  def OnClose(self, evt):
    self._onSave()
    evt.Skip()
  #------------------------------------------------------------------
  #
  def _onToolClick(self, evt):
    if evt.GetId() == self.ID_SAVEFILE: self._onSave(force=True)
    elif evt.GetId() == self.ID_SAVEFILE_AS: self._onSaveAs()
    elif evt.GetId() == self.ID_OPENFILE: self._onLoad()
  #------------------------------------------------------------------
  #
  def _onKeyPressed(self, evt):
    if self.tbar.GetToolEnabled(self.ID_SAVEFILE) != self.editor.GetModify():
      self.tbar.EnableTool(self.ID_SAVEFILE, self.editor.GetModify())
      self.tbar.Refresh()
    keycode, readchar=self.editor.processKey(evt)
    #
    if evt.ControlDown():
      if (readchar == 'S') and evt.ControlDown():
        if self.saveFile(self._filepath): return
    #
    self.OnKeyPressed(evt, keycode, readchar)
  #------------------------------------------------------------------
  #
  def OnKeyPressed(self, evt, keycode, readchar):
    '''override'''
    evt.Skip()
  #------------------------------------------------------------------
  #
  def SetText(self, text): self.editor.SetText(text)
  #------------------------------------------------------------------
  #
  def _onSave(self, evt=None, force=False):
    if self.nosave: return
    if self.editor.GetModify():
      if not force:
        print "Parent is", self.parent
        if not wxut.questionbox("The text has changed.\nWanna save it?", self.parent):
          return
      self.saveFile(self._filepath)
  #------------------------------------------------------------------
  #
  def _onSaveAs(self, evt=None):
    self.saveFile(os.path.dirname(self._filepath))
    self.parent.SetTitle(os.path.basename(self._filepath))
  #------------------------------------------------------------------
  #
  def saveFile(self, filepath="", force=False):
    if (not force) and (not os.path.isfile(filepath)):
      filepath=wxut.saveFileDialog(start=self._filepath)
    if filepath:
      self.editor.SaveFile(filepath)
      self.tbar.EnableTool(self.ID_SAVEFILE, False)
      self._filepath=filepath
      return True
    return False
  #------------------------------------------------------------------
  #
  def _onLoad(self):
    self.loadFile()
  #------------------------------------------------------------------
  #
  def loadFile(self, filepath="", wildcard="*"):
    self._onSave()
    if not os.path.isfile(filepath):
        filepath=wxut.openFileDialog(
          wildcard=wildcard,
          start=os.path.dirname(filepath or self._filepath)
      )
    filepath=os.path.abspath(filepath)
    if os.path.isfile(filepath):
      #change lexer according with the file extension
      ext=os.path.splitext(filepath)[1][1:]
      self.changeLexer(self.ext2lex.get(ext, 'HTML'))
      #
      self.editor.LoadFile(filepath)
      self._filepath=filepath
      self.parent.SetTitle(os.path.basename(self._filepath))
      self.status.SetStatusText("File '%s' loaded."%filepath)
      self.filename=filepath
      self.editor.SetFocus()
    else:
        self.filename=None
  #------------------------------------------------------------------
  #
  def changeLexer(self, lexer):
    self.editor.changeLexer(lexer)
#=======================================================================
#
class mupuEdAlone(wx.Frame, mupuEd):
  '''subclass it for use mupuEd as a stand-alone frame window
  '''
  #------------------------------------------------------------------
  #
  def __init__(self, parent=None, title="mupuEdAlone", pos=(0,0), size=(700,500), lexer="AUTO"):
    wx.Frame.__init__(self, parent, -1, title, pos=pos, size=size)
    mupuEd.__init__(self, self)
    self.changeLexer(lexer)
#=======================================================================
#
class mupuEdChild(wx.Panel, mupuEd):
  '''subclass it for use mupuEd as a child of a wx window component
  '''
  def __init__(self, parent=None):
    wx.Panel.__init__(self, parent)
    mupuEd.__init__(self, self)
  #------------------------------------------------------------------
  #
  def SetTitle(self, title):
    if self.GetParent():
      if 'SetTitle' in self.GetParent().__dict__:
        self.GetParent().SetTitle(title)
#=======================================================================
# MAIN
#=======================================================================
if __name__ == "__main__":
  class MyApp(wx.App):
    def OnInit(self):
      win=mupuEdAlone(None)
      win.Show(True)
      self.SetTopWindow(win)
      return True
  app = MyApp(0)
  app.MainLoop()
