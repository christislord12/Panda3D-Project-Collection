"""

    This file holds complex controls
    that are composed of multiple widgets

"""
from widgets import *

class Holder(GUI,Widget):
    """ like a pane but does not clip its children """


    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        """ creates a holder """
        Widget.__init__(self,pos,size)
        self.things = []


    def add(self,thing):
        """ adds childred elements to the holder """
        self.things.append(thing)
        thing.reparentTo(self.node)
        thing.parent = self
        return thing

    def reSize(self,size=None):
        """ does nothing on resize """

    def reparentTo(self,node):
        """ reparents this holder to a node """
        self.node.reparentTo(node)

    def update(self):
        """ when it is opned """

    def do(self):
        """ every one in awhile """

    def draw(self,pos,size):
        """ draws the children of this holder """
        gui.theme.fixZ(self)
        GUI.draw(self,pos,size)

    def clear(self):
        for thing in self.things:
            thing.node.removeNode()
        self.things = []

class Pane(Holder):

    """ pane is a holder that clips its elements """

    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        """ creates a pane """
        Widget.__init__(self,pos,size)
        self.things = []
        self.clipper = Clipper(self.pos,self.size)
        self.canvis = self.clipper.node()
        self.canvis.reparentTo(self.node)
        #self.canvis.setPos(0,0,10)
        self.clipper.resize()

    def add(self,thing):
        """ adds childred elements to the holder """
        self.things.append(thing)
        thing.reparentTo(self.canvis)
        thing.parent = self
        return thing

    def draw(self,pos,size):
        """ draws the children of this holder and clips them"""
        gui.theme.fixZ(self)
        self.clipper.pos = self.pos+pos
        self.clipper.size = self.size
        self.clipper.resize()
        GUI.draw(self,pos,size)


class Frame(Pane):

    """
        Frame has a frame border around it and no extra controls
    """

    skinType = "FRAME"
    dropGeom = 0

    def draw(self,pos,size):
        """ update the frame represintaion """
        if self.geom == None or self.regenerate:
            if self.geom:
                self.geom.removeNode()
            if self.skinType:
                box = (self.skinType, Vec2(0,0),self.size,self)
                self.geom = gui.theme.generate(box)
                if self.geom:
                    self.geom.reparentTo(self.node)
                    self.geom.setZ(self.dropGeom)
        self.regenerate = False
        Pane.draw(self,pos,size)

    def mouseEvent(self,key,mouse):
        """ on mouse event pass it down to the children """
        Pane.mouseEvent(self,key,mouse)
        self.onClick(self,key,mouse)
        return True

    def onClick(self,button,key,mouse):
        """ frames consume mouse clicks """
        return False

class SlideVBar(Frame):
    """
        Vertical bar chart like button
    """
    skinType = None

    def __init__(self,*args,**kargs):
        if "onChange" in kargs:
            self.onChange = kargs["onChange"]
            del kargs["onChange"]
        Frame.__init__(self,*args,**kargs)
        self.w = self.add(Button("",pos=Vec2(0,0),size=self.size,onClick=self.onClick))
        self.w.skinType = "INPUT"

    def onClick(self,button,key,mouse):
        """ changes the value """
        self.setValue((self.size[1]-mouse.getY())/self.size.getY())

    def setValue(self,value):
        """ sets the value of the slide button """
        self.value = value
        #self.setText(str(int(value))+"%")
        self.w.size.setY(value*self.size.getY())
        self.w.pos.setY(self.size[1] - value*self.size.getY())
        self.w.setPos(self.w.pos)
        self.w.regenerate = True
        gui.redraw()
        self.onChange(self)

    def onChane(self,button):
        """ overide this method to get the change event """


class SlideHBar(Frame):
    """
        Horizontal bar chart like button
    """

    skinType = None

    def __init__(self,*args,**kargs):
        if "onChange" in kargs:
            self.onChange = kargs["onChange"]
            del kargs["onChange"]
        Frame.__init__(self,*args,**kargs)
        self.w = self.add(Button("",pos=Vec2(0,0),size=self.size,onClick=self.onClick))
        self.w.skinType = "INPUT"

    def onClick(self,button,key,mouse):
        """ changes the value """
        self.setValue(mouse.getX()/self.size.getX())

    def setValue(self,value):
        """ sets the value of the slide button """
        self.value = value
        #self.setText(str(int(value))+"%")
        self.w.size.setX(value*self.size.getX())
        self.w.regenerate = True
        gui.redraw()
        self.onChange(self)

    def onChange(self,button):
        """ overide this method to get the change event """

class VScroll(Frame):
    """
        Vertical scroll bar
    """

    skinType = "VSCROLL"

    def __init__(self,pos=Vec2(0,0),size=Vec2(10,100)):
        Frame.__init__(self,pos,size)
        self.bar = self.add(Button("",pos=Vec2(0,0),size=size,onClick=self.scrollbarClick))
        self.bar.skinType = "VSCROLL"
        self.up = self.add(Button("",pos=Vec2(0,0),size=Vec2(10,10),onClick=self.scrollUp))
        self.down = self.add(Button("",pos=Vec2(0,size[1]-10),size=Vec2(10,10),onClick=self.scrollDown))
        #self.center = self.add(Button("",pos=Vec2(0,size[1]/2-10),size=Vec2(10,40)))
        self.center = self.add(Button("",pos=Vec2(0,0),size=Vec2(10,40)))
        self.center.onClick = self.onCenterDrag
        self.up.skinType = "VSCROLL_UP"
        self.down.skinType = "VSCROLL_DOWN"
        self.center.skinType = "VSCROLL_CENTER"
        self.value = 0.0
        self.onScrollNotifier = None

    def onCenterDrag(self,button,key,mouse):
        self.center.onDrag(button,key,mouse)
        gui.dragFun = self.onScrollBase

    def scrollbarClick(self,button,key,mouse):
        self.center.setPos(Vec2(0, mouse.getY()-20))
        self.center.regenerate=True
        self.onScrollBase()

    def scrollUp(self,*args):
        self.center.pos += Vec2(0,-10)
        self.onScrollBase()

    def scrollDown(self,*args):
        self.center.pos += Vec2(0,10)
        self.onScrollBase()

    def setValue(self,value):
        self.value = value
        s = float(self.size[1]-40)
        self.center.setPos(Vec2(0,value*s))
        #self.onScroll(value)
        self.center.regenerate=True
        self.onScrollBase()
        #gui.redraw()

    def getValue(self):
        return self.value

    def onScrollBase(self,*args):
        s = float(self.size[1]-40)
        value = min(s,max(0,self.center.pos[1]))/s
        #print value
        self.center.setPos(Vec2(0,value*s))
        if abs(self.value - value) > .0005:
            #print "blink"
            self.value = value
            self.onScroll(value)
            if self.onScrollNotifier:
                self.onScrollNotifier(self, value)
            self.center.regenerate=True
            gui.redraw()

    def onScroll(self,value):
        pass

class HScroll(Frame):

    """
        Horizontal scroll bar
    """

    skinType = "HSCROLL"

    def __init__(self,pos=Vec2(0,0),size=Vec2(10,100)):
        Frame.__init__(self,pos,size)
        self.bar = self.add(Button("",pos=Vec2(0,0),size=size,onClick=self.scrollbarClick))
        self.bar.skinType = "HSCROLL"

        self.up = self.add(Button("",pos=Vec2(0,0),size=Vec2(10,10),onClick=self.scrollUp))
        self.down = self.add(Button("",pos=Vec2(size[0]-10,0),size=Vec2(10,10),onClick=self.scrollDown))
        #self.center = self.add(Button("",pos=Vec2(size[0]/2-10,0),size=Vec2(40,10)))
        self.center = self.add(Button("",pos=Vec2(0,0),size=Vec2(40,10)))
        self.center.onClick = self.onCenterDrag
        self.up.skinType = "HSCROLL_UP"
        self.down.skinType = "HSCROLL_DOWN"
        self.center.skinType = "HSCROLL_CENTER"
        self.value = 0.0
        self.onScrollNotifier = None

    def onCenterDrag(self,button,key,mouse):
        self.center.onDrag(button,key,mouse)
        gui.dragFun = self.onScrollBase

    def scrollbarClick(self,button,key,mouse):
        #if mouse.getX() < self.center.getPos().getX():
        #    self.scrollUp()
        #else:
        #    self.scrollDown()
        self.center.setPos(Vec2(mouse.getX()-20,0))
        self.center.regenerate=True
        self.onScrollBase()

    def scrollUp(self,*args):
        self.center.pos += Vec2(-10,0)
        self.onScrollBase()

    def scrollDown(self,*args):
        self.center.pos += Vec2(10,0)
        self.onScrollBase()

    def setValue(self,value):
        self.value = value
        s = float(self.size[0]-40)
        self.center.setPos(Vec2(self.value*s,0))
        self.center.regenerate=True
        self.onScrollBase()
        #gui.redraw()

    def getValue(self):
        return self.value

    def onScrollBase(self,*args):
        s = float(self.size[0]-40)
        value = min(s,max(0,self.center.pos[0]))/s
        self.center.setPos(Vec2(value*s,0))
        if abs(self.value - value) > .0005:
            self.value = value
            self.onScroll(value)
            if self.onScrollNotifier:
                self.onScrollNotifier(self, value)
            self.center.regenerate=True
            gui.redraw()

    def onScroll(self,value):
        pass


class HSlider(Frame):

    """
        Horizontal slider bar
    """

    skinType = "HSLIDER"

    def __init__(self,pos=Vec2(0,0),size=Vec2(10,100)):
        Frame.__init__(self,pos,size)
        self.bar = self.add(Button("",pos=Vec2(0,0),size=size,onClick=self.scrollbarClick))
        self.bar.skinType = "HSLIDER"

        self.center = self.add(Button("",pos=Vec2(0,0),size=Vec2(40,10)))
        self.center.onClick = self.onCenterDrag
        self.center.skinType = "HSCROLL_CENTER"
        self.value = 0.0
        self.onScrollNotifier = None

    def onCenterDrag(self,button,key,mouse):
        self.center.onDrag(button,key,mouse)
        gui.dragFun = self.onScrollBase

    def scrollbarClick(self,button,key,mouse):
        self.center.setPos(Vec2(mouse.getX()-20,0))
        self.center.regenerate=True
        self.onScrollBase()

    def setValue(self,value):
        self.value = value
        s = float(self.size[0]-40)
        self.center.setPos(Vec2(self.value*s,0))
        self.center.regenerate=True
        self.onScrollBase()
        #gui.redraw()

    def getValue(self):
        return self.value

    def onScrollBase(self,*args):
        s = float(self.size[0]-40)
        value = min(s,max(0,self.center.pos[0]))/s
        self.center.setPos(Vec2(value*s,0))
        if abs(self.value - value) > .0005:
            self.value = value
            self.onScroll(value)
            if self.onScrollNotifier:
                self.onScrollNotifier(self, value)
            self.center.regenerate=True
            gui.redraw()

    def onScroll(self,value):
        pass


class ScrollPane(Holder):
    """
        This is used to put stuff inside and scroll around them
    """
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        Holder.__init__(self,pos,size)
        self.h = self.add(HScroll(Vec2(0,size[1]-10),size=Vec2(size[0]-10,10)))
        self.v = self.add(VScroll(Vec2(size[0]-10,0),size=Vec2(10,size[1]-10)))
        self.p = self.add(Pane(Vec2(0,0),size=Vec2(size[0]-10,size[1]-10)))
        self.innerHolder = self.p.add(Holder(size=Vec2(100000,100000)))
        self.h.onScroll = self.onScroll
        self.v.onScroll = self.onScroll
        self.h.setValue(0)
        self.v.setValue(0)
        self.add = self.innerHolder.add
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0

    def _computeMinMax(self):
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        for thing in self.innerHolder.things:
            self.minX = min(thing.getPos().getX(),self.minX)
            self.minY = min(thing.getPos().getY(),self.minY)
            self.maxX = max(thing.getPos().getX()+thing.size.getX(),self.maxX)
            self.maxY = max(thing.getPos().getY()+thing.size.getY(),self.maxY)

    def onScroll(self,value):
        self._computeMinMax()
        xrange = max(0,self.maxX - self.minX - self.size.getX())
        yrange = max(0,self.maxY - self.minY - self.size.getY()+40)
        #print "range",xrange,yrange
        #print "value",self.h.value,self.v.value
        #print "final",xrange-self.h.value*xrange,yrange-self.v.value*yrange
        self.innerHolder.setPos(
            Vec2(xrange-self.h.value*xrange,
                 -self.v.value*yrange))
        gui.redraw()

    def clear(self):
        self.innerHolder.clear()
        self.h.setValue(0)
        self.v.setValue(0)
        self.onScroll(0)
        #Holder.clear(self)

class SelectListBase(ScrollPane):
    """ creates a scroll pane with selectable buttons """
    SINGLE_SELECT = 1
    MULTI_SELECT = 2
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100),options=[]):
        ScrollPane.__init__(self,pos,size)

        self.itemlist = []
        for i,option in enumerate(options):
            button = Button(option, Vec2(0,10+int(i)*20),Vec2(size[0],20),onClick=self.optionSelect)
            button.skinType = "SELECT_BG"
            button.id = i
            self.add(button)
            self.itemlist.append(button)

        self.selected = []
        self.mode = self.SINGLE_SELECT

    def setMode(self, mode):
        self.mode = mode

    def optionSelect(self, button,key,mouse):
        if self.mode == self.SINGLE_SELECT:
            if button in self.selected:
                return

            for b in self.selected:
                b.skinType = "SELECT_BG"
                b.textNode.setColor(Vec4(1,1,1,1))
                b.regenerate = True
            self.selected = []

        """ selects an option """
        #option = button.getText()
        if button in self.selected:
            button.skinType = "SELECT_BG"
            self.selected.remove(button)
            button.textNode.setColor(Vec4(1,1,1,1))
        else:
            button.skinType = "SELECT_HIGHLIGHT"
            self.selected.append(button)
            button.textNode.setColor(Vec4(1,0,0,0))#*gui.theme.SELECT_OPTION_COLOR))
        button.regenerate = True
        gui.redraw()
        self.onSelect(button.id)
        return True

    def addItem(self, item):
        i = len(self.itemlist)
        button = Button(item, Vec2(0,10+int(i)*20),Vec2(self.size[0],20),onClick=self.optionSelect)
        button.skinType = "SELECT_BG"
        button.id = i
        self.add(button)
        self.itemlist.append(button)

    def onSelect(self, i):
        """ sub class this """


class vSelectList(SelectListBase):
    """ creates a scroll pane with selectable buttons """
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100),options=[]):
        SelectListBase.__init__(self,pos=pos,size=size,options=options)
        self.listener = None

    def setListener(self, listener):
        self.listener = listener

    def onSelect(self, i):
        if self.listener != None:
            taskMgr.doMethodLater(0.1, self.listener, "selectlisttask", extraArgs=[i])

    def DeselectAll(self):
        for button in self.selected:
            button.skinType = "SELECT_BG"
            button.textNode.setColor(Vec4(1,1,1,1))
            button.regenerate = True
        gui.redraw()
        self.selected = []

    def Clear(self):
        self.h.setValue(0.0)
        self.v.setValue(0.0)
        self.selected = []
        for button in self.itemlist:
            self.innerHolder.things.remove(button)
            button.destroy()
        self.itemlist = []
        self.onScroll(0)
        gui.redraw()

class Form(Frame):
    """
        This is the standard window of the windowing system
        use this as the top holder for most of the controls
        this should be added to the main gui object

    """
    skinType = "FORM"
    dropGeom = 20

    def __init__(self,title,pos=Vec2(200,200),size=Vec2(200,300)):
        Frame.__init__(self,pos,size)
        self.minSize = Vec2(100,30)
        self.things = []
        self.title = title
        size1 = Vec2(self.size[0]-40,20)
        self.titlebutton=Button(self.title,
            pos=Vec2(20,0),
            size=size1,
            onClick=self.startDrag)
        self.bar = Frame.add(self,self.titlebutton)

        self.openbutton=Button("",
            pos=Vec2(size1[0]-5,5),
            size=Vec2(10,10),
            onClick=self.iconize)
        self.openbutton.skinType = "WUP"

        Frame.add(self,self.openbutton)

        self.x = Frame.add(self,Button("",pos=Vec2(self.size[0]-30,5),size=Vec2(10,10),onClick=self.onClose));
        self.x.skinType = "X"
        self.bar.skinType = "FRAMEBAR"
        #self.sizer = Frame.add(self,Button("",pos=self.size-Vec2(20,20),size=Vec2(20,20),onClick=self.startResize));
        #self.sizer.skinType = "DRAG"
        self.open = True
        self.orginalSize = self.size

    def iconize(self,button,key,mouse):
        self.open = not self.open
        if self.open:
            skin = "WUP"
            FSkin = "FORM"
            self.setSize(self.orginalSize)
        else:
            skin = "WDOWN"
            FSkin = "XXX"
            self.setSize(Vec2(self.size[0], 20))
        self.openbutton.skinType = skin
        self.openbutton.regenerate = True
        self.skinType = FSkin
        self.regenerate = True
        gui.redraw()

    def setTitle(self, title):
        self.title = title
        self.titlebutton.setText(title)

    def startDrag(self,button,key,mouse):
        self.onDrag(button,key,mouse+Vec2(+20,0))

    def startResize(self,button,keys,mouse):
        """ called when the form is begining to be reized """
        self.sizer.onDrag(button,keys,mouse)
        gui.dragFun = self.onResize

    def onClose(self,button,key,mouse):
        """ called when the form is closing """
        self.node.hide()

    def setSize(self,size):
        self.size = size
        self.bar.size = Vec2(min(200,self.size[0]-40),20)
        #self.sizer.setPos( self.size-Vec2(20,20) )
        self.x.setPos( Vec2(self.size[0]-30,5) )
        Frame.setSize(self,size)

##    def onResize111(self,window=None):
##        """ called when the form should resize """
##        delta = self.size - (self.sizer.pos+Vec2(20,20))
##        self.size = self.sizer.pos+Vec2(20,20)
##        if self.size[0] < self.minSize[0]:
##            self.size.setX(self.minSize[0])
##        if self.size[1] < self.minSize[1]:
##            self.size.setY(self.minSize[1])
##        self.bar.size = Vec2(self.size[0]-40,10)
##        self.sizer.setPos( self.size-Vec2(20,20) )
##        self.x.setPos( Vec2(self.size[0]-30,5) )
##        self.sizer.pos=self.size-Vec2(10,10)
##        if delta.length() > 1:
##            self.regenerate = True
##            gui.redraw()

    def toggle(self):
        """ hids or shows this thing """
        if self.node.isHidden():
            self.node.show()
        else:
            self.node.hide()


class GridForm(Form):

    """
        This quickly created crud like interfaces with
        descrition on one side and and widgets on the other
    """

    def __init__(self,title,pos=Vec2(300,200),size=Vec2(200,300),labelWidth=100):
        Form.__init__(self,title,pos,size)
        self.currentY = 30
        self.labelWidth = labelWidth

    def add(self,label,thing):
        """ requires a label when adding a widgit """
        thing = Frame.add(self,thing)
        thing.pos = Vec2(self.labelWidth,self.currentY)
        thing.setPos(thing.pos)
        label = Frame.add(self,Label(label,pos=Vec2(0,self.currentY)))
        self.currentY+=20
        #self.size = Vec2(300,max(100,self.currentY+20))
        #self.sizer.setPos( self.size-Vec2(20,20) )
        #self.onResize()
        #self.regenerate = True
        #gui.redraw()
        return thing

    def clear(self):
        Form.clear(self)
        self.currentY = 30

class Menu(Frame):
    """
        Creates an interesting style menu that has all of its drop downs horisontal
    """
    skinType = None

    def __init__(self,title,options,pos=Vec2(0,0),size=Vec2(200,300)):
        """ options are in a form of  name,funciton,arguments """
        Frame.__init__(self,pos,Vec2(160,10+20*len(options)))
        self.options = options
        i = 0
        for (name,fun,args) in self.options:
            button = Button(name, Vec2(0,10+int(i)*20),Vec2(160,16),onClick=self.menuSelect)
            self.add(button)
            i += 1

    def menuSelect(self,button,keys,mouse):
        """ called when one of the menus have been selected """
        for (name,fun,args) in self.options:
            if button.getText() == name and fun:
                fun(*args)

