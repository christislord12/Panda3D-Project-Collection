"""
    This containts the widgits the the tree gui system
    the widgits cannot contain other other widgits and are
    the basic building blocks
"""
from pandac.PandaModules import *
from core import GUI,Clipper

def curry(func, *args, **kwds):
    def callit(*moreargs, **morekwds):
        kw = kwds.copy()
        kw.update(morekwds)
        return func(*(moreargs+args), **kw)
    return callit

class Widget(object):
    """
        Base widgest for all widgets
    """
    skinType = None
    canTab = False

    def __init__(self,pos=Vec2(0,0),size=Vec2(0,0)):
        """ you probably do not want to create a plain widgits
            but use of its derivitives """
        self.pos = pos
        self.size = Vec2(size)
        self.node = NodePath(self.__class__.__name__)
        self.node.setPos(pos[0],0,pos[1])
        self.geom = None
        self.regenerate = True

    def setSize(self,size):
        """ sets the size """
        self.size = Vec2(size[0],size[1])
        self.regenerate = True
        gui.redraw()

    def getSize(self):
        """ gets the size of the object """
        return self.size

    def setPos(self,pos):
        """ sets the positoins of the gui object """
        self.pos = Vec2(pos[0],pos[1])
        self.node.setPos(pos[0],0,pos[1])

    def onDrag(self,button,key,mouse):
        """ this function will start to drug the window """
        gui.drag = self
        gui.dragPos = self.pos-gui.mouse
        self.parent.toFront(self)

    def getPos(self):
        """
            returns the positions of the widgit relative to
            its parent
        """
        return self.pos

    def resize(self):
        """
            resizes the gui object (many objects cant be
            resized so in this case the functions does
            nothing
        """

    def draw(self,pos,size):
        """ modifys the geometry of the object """
        if self.regenerate:
            self.regenerate = False
            if self.geom:
                self.geom.removeNode()
            if self.skinType:
                box = (self.skinType, Vec2(0,0),self.size,self)
                self.geom = gui.theme.generate(box)
                if self.geom:
                    self.geom.reparentTo(self.node)
        gui.theme.fixZ(self)

    def __str__(self):
        """ returns the string representaion of the object """
        v1,v2 = "",""
        try: v1 = str(self.value)
        except:pass
        try: v2 = str(self.getText())
        except:pass
        return "<%s %s %s>"%( self.__class__.__name__, v2, v1 )

    def reparentTo(self,node):
        """ attaches the gui object to a different node """
        self.node.reparentTo(node)

    def mouseEvent(self,key,mouse):
        """ Override this for your mouse event """

    def getNode(self):
        """ returs the under laying node of the object """
        return self.node


    def update(self):
        """
            this is called every second as a
            convince for updaing the readout stats
            override
        """

    def hide(self):
        """ hides widget """
        self.node.hide()

    def show(self):
        """ shows widget """
        self.node.show()

    def onFocus(self):
        """ when the input gains focus """

    def onUnFocus(self):
        """ when the input looses focus """

    def destroy(self):
        self.node.removeNode()

class Label(Widget):

    """ use this for short pice of static text """

    def __init__(self,textstring,pos=Vec2(0,0),point=14):
        """ create a gui label """
        Widget.__init__(self,pos)
        self.text = TextNode("text")
        self.text.setCardDecal(True)
        self.currentString = textstring
        self.text.setText(textstring)
        self.text.setTextColor(*gui.theme.LABELCOLOR)
        self.textNode = self.node.attachNewNode(self.text)
        self.textNode.setScale(Vec3(point,1,-point))
        self.textNode.setPos(0,0,point)

    def setText(self,textstring):
        """ sets the text of the object """
        textstring = str(textstring)
        if self.currentString != textstring:
            self.currentString = textstring
            self.text.setText(textstring)

    def getText(self):
        """ gest the text """
        return self.text.getText()

class Text(Label):

    """ use this for long pice of dynamic text """

    def __init__(self,textstring,pos=Vec2(0,0),wrap=5,point=14):
        """ create a gui label """
        Label.__init__(self,textstring,pos,point=point)
        self.text.setWordwrap(wrap)


class BaseInput(Label):
    """ this is the most primitive input widget """

    skinType = "INPUT"
    canTab = True

    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,20),point=14):
        """ create a gui input """
        Label.__init__(self,textstring,pos)
        self.size = Vec2(size)

    def mouseEvent(self,key,mouse):
        """ mouse events are usd to focus the Base Input """
        gui.keys.focus = self
        return True

    def setText(self,textstring):
        """ sets the text of the input """
        self.text.setText(str(textstring))

    def onKey(self,key):
        """ figure out what to do with the key after you get it """
        text = self.text.getText()

        if key == "backspace":
                self.text.setText( text[0:-1] )
        elif key == "enter":
            self.onEnter(self)
        elif key == "space":
            self.text.setText( text + ' ' )
        else:
            self.text.setText( text + key )
        return True

    def onEnter(self,key):
        """ overide this """


class Input(BaseInput):

    """ much better input widget """

    skinType = "INPUT"

    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,20),point=14):
        """ create a gui input """
        #from direct.gui.DirectGui import DirectEntry
        Widget.__init__(self,pos,size)
        textstring = str(textstring)
        self.entry = PGEntry(textstring)
        self.entry.setup(30*.45,1)
        self.entry.setText(textstring)

        style = PGFrameStyle()
        style.setType(PGFrameStyle.TNone)
        self.entry.setFrameStyle(0,style)
        self.entry.setFrameStyle(1,style)

        self.realTextNode = self.entry.getTextNode()
        self.realTextNode.setTextColor(1,1,1,1)
        crusor = self.entry.getCursorDef().node()
        crusor.setAttrib(ColorAttrib.makeFlat(Vec4(1,1,1,1)),100)

        self.textNode = NodePath(self.entry)
        self.textNode.setScale(point,1,-point)
        self.textNode.setPos(0,0,point)
        self.textNode.reparentTo(self.node)


    def mouseEvent(self,key,mouse):
        """ handes mouse events """
        gui.keys.focus = self
        self.textNode['focus'] = True
        return True

    def onFocus(self):
        """ when the input gains focus """
        gui.keys.focus = self
        self.entry.setFocus(True)
        self.entry.setCursorPosition(len(self.entry.getText()))

    def onUnFocus(self):
        """ when the input looses focus """
        gui.keys.focus = None
        self.entry.setFocus(False)
        self.node.setColor(1,1,1,1)
        #self.entry.setCursorPosition(len(self.textNode.get())-1)
        #self.textNode['focus'] = False


    def onKey(self,key):
        """ when it gets a key """
        if key == "enter":
            self.onEnter(self)
        return True

    def draw(self,*arg):
        """ updates the input object """
        if gui.keys.focus != self:
            self.entry.setFocus(False)
        if self.regenerate:
            #self.textNode['text_fg'] = Vec4(*gui.theme.LABELCOLOR)
            pass
        self.textNode.reparentTo(self.node)
        BaseInput.draw(self,*arg)

    def _onEnter(self,txt):
        """ low level on enter event"""
        self.onEnter(self)

    def setText(self,textstring):
        """ sets the text of the input """
        self.entry.setText(str(textstring))

    def getText(self):
        """ get the text of the input """
        return self.entry.getText()

    def mouseEvent(self,key,mouse):
        """ when the users does some thing with a mouse """
        self.onFocus()
        return True

#Input = BaseInput

class Password(Input):
     def __init__(self,*args,**kargs):
         Input.__init__(self,*args,**kargs)
         #self.entry.setObscureMode(True)

class Button(Label):

    """ standard button """

    skinType = "BUTTON"

    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,16),point=14,onClick=None):
        """ create a gui input """
        Label.__init__(self,textstring,pos,point)
        self.size = size
        if onClick:
            self.onClick = onClick

    def mouseEvent(self,key,mouse):
        """ do what button does best """
        try:
            self.onClick(self,key,mouse)
        except TypeError,e:
            print str(e)
            if "takes" in str(e) and "argument" in str(e) :
                self.onClick()
            else:
                raise
        return True

    def onClick(self,button,key,mouse):
        """ overdie this """
        self.regenerate = True

class ProgressBar(Label):

    skinType = "PROGRESS_BAR"

    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,16),point=14,onClick=None):
        """ create a gui input """
        Label.__init__(self,textstring,pos,point)
        self.value = 0
        self.maxSize = size
        self.size = Vec2(0,size.getY())
        self.size.setX(size.getX()*self.value)

    def setValue(self,value):
        """ sets the value of the progress bar """
        self.value = value
        self.size.setX(self.maxSize.getX()*self.value)
        self.regenerate = True
        gui.redraw()

class Radio(Button):
    """
        radio button ... only one button of this
        type can be selected in a given parent
    """
    skinType = "RADIOOFF"
    value = False
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(20,20),point=14,onClick=None):
        """ creates a radio button (all radio buttons attached to the parent
            will switch when one is clicked on """
        Button.__init__(self," "*10+textstring,pos,size,point,onClick)

    def onClick(self,button,key,mouse):
        """
            changes the state of the radio and
            changaes the state of the radio buttons
            around it
        """
        self.regenerate = True
        for thing in self.parent.things:
            if thing.__class__ == self.__class__:
                thing.value = False
                thing.regenerate = True
                thing.skinType = "RADIOOFF"
        self.value = not self.value
        if self.value:
            self.skinType = "RADIOON"
        else:
            self.skinType = "RADIOOFF"


class Check(Button):
    """
        Standard on/off button
    """
    skinType = "CHECKOFF"
    value = False

    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(20,20),point=14,value=False,onClick=None):
        """ creates a check box """
        self.value = value
        if self.value:
            self.skinType = "CHECKON"
        else:
            self.skinType = "CHECKOFF"
        Button.__init__(self," "*10+textstring,pos,size,point,self.onClick)
        self.onClickHandler = onClick

    def onClick(self,button,key,mouse):
        """ checks or uncecks the button value """
        self.regenerate = True
        self.value = not self.value
        if self.value:
            self.skinType = "CHECKON"
        else:
            self.skinType = "CHECKOFF"
        if self.onClickHandler:
            self.onClickHandler(self)

class Icon(Button):
    """ a button that represents an image """

    skinType = None

    def __init__(self,pos=Vec2(0,0),size=Vec2(20,20),point=14,onClick=None):
        """ creates a clikcable icon object """
        Button.__init__(self,"",pos,size,point,onClick)


class RealIcon(Button):
    """ a button that represents an image """

    skinType = None

    def __init__(self,iconFile,iconRec,pos=Vec2(0,0),size=None,point=14,onClick=None,):
        """ creates a clikcable icon object """
        Button.__init__(self,"",pos,size,point,onClick)
        self.iconFile = loader.loadTexture(iconFile)
        self.node.setTexture(self.iconFile)
        self.node.setTransparency(True)
        self.uvPos = Vec2(iconRec[0],iconRec[1])
        self.uvSize = Vec2(iconRec[2],iconRec[3])
        if size == None:
            self.size = self.uvSize
        else:
            self.size = size

    def setIconRec(self,iconRec):
        uvPos = Vec2(iconRec[0],iconRec[1])
        uvSize = Vec2(iconRec[2],iconRec[3])
        if uvPos == self.uvPos and uvSize == self.uvSize:
            return # no changes there
        self.uvPos = uvPos
        self.uvSize = uvSize
        self.regenerate = True

    def draw(self,pos,size):
        """ generate geometry of the object """
        if self.regenerate:
            self.regenerate = False
            if self.geom:
                self.geom.removeNode()
            box = (self.skinType, Vec2(0,0),self.size,self)
            self.geom = gui.theme.drawSimple(
                self.size[0],self.size[1],
                self.uvPos[0],self.uvPos[1],
                self.uvSize[0],self.uvSize[1],
                self.iconFile.getXSize(),self.iconFile.getYSize())
            self.geom.reparentTo(self.node)
        gui.theme.fixZ(self)