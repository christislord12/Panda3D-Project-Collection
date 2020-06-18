import math, inspect,operator
#from pandac.PandaModules import *
from gui.core import GUI
from gui.theme import Theme
from gui.controls import vSelectList,Form,Vec2,Label,Button,ScrollPane,Form,Check,HSlider,Frame
import demobase
##def makeTextureCardNp(name, textfile):
##    maker = CardMaker( name )
##    maker.setFrame( 0, 1, 0, 1)
##    #maker.setUvRange(Point2(0,0), Point2(0,0))
##    #maker.setUvRange(Point2(1,1), Point2(1,1))
##    np = NodePath(maker.generate())
##    tex = loader.loadTexture(textfile)
##    np.setTexture(tex,1)
##    return np


# create main gui class
GUI(theme=Theme("gui/data/newgui1.png"))

def getPos(row):
    return 23 * (row)

class MainWin():
    labelWidth = 50
    def __init__(self, myparent):
        self.myparent = myparent

        self.demoForm = Form("Actions",pos=Vec2(20,45),size=Vec2(200,500))
        self.demoList = vSelectList(pos=Vec2(10,30),size=Vec2(190,470))
        self.demoList.setListener(self.actionSelected)
        self.demoForm.add(self.demoList)
        gui.add(self.demoForm)


        self.functionForm = Form("Functions",pos=Vec2(270,45),size=Vec2(200,500))

        self.basicsList = vSelectList(pos=Vec2(10,30),size=Vec2(190,200))
        self.basicsList.setListener(self.basicsSelected)
        self.functionForm.add(self.basicsList)

        self.functionList = vSelectList(pos=Vec2(10,250),size=Vec2(190,250))
        self.functionList.setListener(self.functionSelected)
        self.functionForm.add(self.functionList)

        gui.add(self.functionForm)

        self.attrForm = Form("Attributes",pos=Vec2(520,45),size=Vec2(250,190))
        self.attrList = vSelectList(pos=Vec2(10,30),size=Vec2(240,170))
        self.attrList.setListener(self.attrSelected)
        self.attrForm.add(self.attrList)
        gui.add(self.attrForm)

        self.attrDetailForm = Form("Attribute Details",pos=Vec2(520,280),size=Vec2(250,265))
        self.attrDetailPane = ScrollPane(pos=Vec2(10,30),size=Vec2(240,235))
        self.attrDetailForm.add(self.attrDetailPane)
        gui.add(self.attrDetailForm)

        self.hide()

    def hide(self):
        self.demoForm.hide()
        self.functionForm.hide()
        self.attrForm.hide()
        self.attrDetailForm.hide()

    def show(self):
        self.demoForm.show()
        self.functionForm.show()
        self.attrForm.show()
        self.attrDetailForm.show()


    def actionSelected(self, i):
        #print i
        #self.demoList.DeselectAll()
        self.SelectDemo(i)
        #self.hide()
        panda = self.myparent.panda.DeactivateGUI()


    def SelectDemo(self, i):
        panda = self.myparent.panda
        if i >= 0:
            if i != self.currentdemo:
                self.basicsList.Clear()
                self.functionList.Clear()
                demoinfo = panda.demolist[i]
                path,mod,demo,title,info = demoinfo
                self.demo = demo
                nr = 0
                self.basics = 0
                for entry in demo.entries:
                    entryname, entryfunction, desc = entry
                    if entryname.find("_base") == 0:
                        self.basics += 1
                        self.basicsList.addItem("%d. %s" % (self.basics, desc))
                    else:
                        nr += 1
                        self.functionList.addItem("%d. %s" % (nr, desc))
                panda.InitDemo(demoinfo)
                self.ClearAttrDetailPanel()
                ## the init demo call is delayed, so it has to be called later
                #self.LoadAttrsPanel()
                self.currentdemo = i
        else:
            self.demoList.DeselectAll()
            if panda != None:
                panda.InitDemo(None)
            self.basicsList.Clear()
            self.functionList.Clear()
            self.attrList.Clear()
            self.ClearAttrDetailPanel()
            self.currentdemo = i

    def ClearDemos(self):
        self.demoList.Clear()

    def LoadDemos(self):
        self.currentdemo = -1
        if self.myparent.panda != None:
            for demoinfo in self.myparent.panda.demolist:
                path,mod,demo,title,info = demoinfo
                self.demoList.addItem(title)
            #self.SelectDemo(-1)

    def basicsSelected(self, j):
        self.executeFunction(j, True)
        self.basicsList.DeselectAll()

    def functionSelected(self, j):
        self.executeFunction(j, False)
        self.functionList.DeselectAll()

    def executeFunction(self, j, basics):
        panda = self.myparent.panda
        if panda != None:
            if not basics:
                j += self.basics

            if True:
                i = self.currentdemo
                panda.ClientAcquire()
                demoinfo = panda.demolist[i]
                path,mod,demo,title,info = demoinfo
                entryname, entryfunction, doc = demo.entries[j]
                try:
                    #print "entry"
                    entryfunction()
                except:
                    traceback.print_exc(file=sys.stdout)

                # give focus to panda window if it is not basic functions
                #if entryname.find("_base") != 0:
                #if not basics:
                #    self.parent.p3dSurfaceFocus()
                panda.ClientRelease()


    def LoadAttrsPanel(self):
        self.attrList.Clear()
        members = inspect.getmembers(self.demo)
        self.attribes = []
        L = []
        for pair in members:
            name,value = pair
            if name.find("att_") == 0 and value != None:
                nodename = value.getNodeName()
                sep = nodename.find(":")

                if sep <= 0:
                    nodename = "App:" + nodename

                #self.attrList.addItem(nodename)
                #self.attribes.append(value)
                L.append((nodename, value))
        sortedlist = sorted(L, key=operator.itemgetter(0))
        node = ""
        for item in sortedlist:
            sep = item[0].find(":")
            head = item[0][0:sep]
            if node != head:
                node = head
                self.attrList.addItem("%s:" % node)
                self.attribes.append(None)
            tail = item[0][sep+1:]
            self.attrList.addItem("     %s" % tail)
            self.attribes.append(item[1])


    def CreateControlFromAttr(self, attribe, row):

        if hasattr(attribe, 'name'):
            name = attribe.name
            i = name.rfind(":")
            if i >= 0:
                name = name[i+1:]

        if attribe.__class__  == demobase.Att_Boolean:
            checkbox = Check(name, pos=Vec2(0,getPos(row)),onClick=self.checkboxHandler,value = attribe.v)
            checkbox.object = attribe
            self.attrDetailPane.add(checkbox)
            return row+1

        if attribe.__class__  in [ demobase.Att_IntRange, demobase.Att_FloatRange]:
            row = self.AddRangePanel(name, attribe, row, demobase.Att_IntRange == attribe.__class__)
            return row

        if attribe.__class__ == demobase.Att_color:
            row = self.AddColorPanel(name, attribe, row)
            return row

        if attribe.__class__ == demobase.Att_Vecs:
            row = self.AddVecPanel(name, attribe, row)
            return row

        # screen if att_ attribute exists
        members = inspect.getmembers(attribe)
        for pair in members:
            name,value = pair
            if name.find("att_") == 0:
                row = self.CreateControlFromAttr(value, row)
        return row

    def ClearAttrDetailPanel(self):
        # clear the panel first
        self.attrDetailPane.clear()


    def attrSelected(self, i):
        self.ClearAttrDetailPanel()
        attribe = self.attribes[i]
        if attribe:
            self.CreateControlFromAttr(attribe, 0)


    def checkboxHandler(self, checkbox):
        if hasattr(checkbox,'object'):
            v = checkbox.value
            checkbox.object.update(v)

    def AddRangePanel(self, name, object, row, fInteger):
        self.attrDetailPane.add(Label(name,pos=Vec2(0,getPos(row))))
        if object.fInteger:
            s = "%d" % object.v
        else:
            s = ("%%0.%df" % (object.precision)) % object.v
        valuelabel = Label(s,pos=Vec2(180,getPos(row+1)))

        self.attrDetailPane.add(valuelabel)
        slider = HSlider(pos=Vec2(10,getPos(row+1)+5), size=Vec2(160,10))
        slider.onScrollNotifier = self.rangeChange
        if object.minv == object.maxv:
            if object.minv == 0:
                slider.minv = -200.0
                slider.maxv = 200.0
            else:
                slider.minv = abs(object.v) * -200.0
                slider.maxv = abs(object.v) * 200.0
        else:
            slider.minv = object.minv
            slider.maxv = object.maxv
        slider.setValue(float(object.v - slider.minv) / float(slider.maxv - slider.minv))

        slider.object = object
        slider.valuelabel = valuelabel
        self.attrDetailPane.add(slider)

        return row+2

    def rangeChange(self, slider, value):
        object = slider.object
        minv = slider.minv
        maxv = slider.maxv
        ov = (maxv - minv) * value + minv
        if object.fInteger:
            ov = int(ov)
            s = "%d" % ov
        else:
            s = ("%%0.%df" % (object.precision)) % ov
        slider.valuelabel.setText(s)
        object.update(ov)

    def AddVecPanel(self, name, object, row):
        self.attrDetailPane.add(Label(name,pos=Vec2(0,getPos(row))))
        row += 1
        l = object.l
        vec = object.getValue()

        if object.minv == object.maxv:
            minv = -200.0
            maxv = 200.0
        else:
            minv = object.minv
            maxv = object.maxv


        for i in range(l):
            v = vec[i]
            if object.fInteger:
                s = "%d" % v
            else:
                s = ("%%0.%df" % (object.precision)) % v
            valuelabel = Label(s,pos=Vec2(180,getPos(row)))

            self.attrDetailPane.add(valuelabel)
            slider = HSlider(pos=Vec2(10,getPos(row)+5), size=Vec2(160,10))
            slider.onScrollNotifier = self.vecChange
            slider.minv = minv
            slider.maxv = maxv
            slider.setValue(float(v - slider.minv) / float(slider.maxv - slider.minv))

            slider.object = object
            slider.index = i
            slider.valuelabel = valuelabel
            self.attrDetailPane.add(slider)
            row += 1

        return row


    def vecChange(self, slider, value):
        object = slider.object
        minv = slider.minv
        maxv = slider.maxv
        ov = (maxv - minv) * value + minv
        if object.fInteger:
            ov = int(ov)
            s = "%d" % ov
        else:
            s = ("%%0.%df" % (object.precision)) % ov
        slider.valuelabel.setText(s)
        object.vec[slider.index].update(ov)


    def AddColorPanel(self, name, object, row):
        self.attrDetailPane.add(Label(name + " - (RGB)",pos=Vec2(0,getPos(row))))
        row += 1
        l = 3
        vec = object.getColor()

        minv = 0.0
        maxv = 1.0

        for i in range(l):
            v = vec[i]
            s = "%0.3f" % v
            valuelabel = Label(s,pos=Vec2(180,getPos(row)))

            self.attrDetailPane.add(valuelabel)
            slider = HSlider(pos=Vec2(10,getPos(row)+5), size=Vec2(160,10))
            slider.onScrollNotifier = self.colorChange
            slider.minv = minv
            slider.maxv = maxv
            slider.setValue(float(v - slider.minv) / float(slider.maxv - slider.minv))

            slider.object = object
            slider.index = i
            slider.valuelabel = valuelabel
            self.attrDetailPane.add(slider)
            row += 1

        return row


    def colorChange(self, slider, value):
        object = slider.object
        minv = slider.minv
        maxv = slider.maxv
        ov = (maxv - minv) * value + minv
        s = "%0.3f" % ov
        slider.valuelabel.setText(s)
        color = object.getColor()
        color[slider.index] = ov
        object.setColor(color)

class Controller():
    WIDTH = 800
    HEIGHT = 600
    def __init__(self, panda):
        self.panda = panda
        self.running = True
        self.active = False
        self.first = True

        # create the message box for later use
        width = int(self.WIDTH * 0.9)
        height = int(self.HEIGHT * 0.4)
        left = (self.WIDTH - width) / 2
        top = (self.HEIGHT - height) / 2
        self.msgForm = Form("Title",pos=Vec2(left,top),size=Vec2(width,height))
        self.messageLabel = Label("", pos=Vec2(0,30), point=18)
        self.msgForm.add(self.messageLabel)
        button = Button("OK",
            pos=Vec2(width/2-10, height-30),
            size=Vec2(20,20),
            onClick=self.closeMsgBox)
        self.msgForm.add(button)

        gui.add(self.msgForm)
        self.msgForm.hide()


        # create a listbox for later use
##        self.listboxForm = Form("Listbox",pos=Vec2(300,45),size=Vec2(200,500))
##        self.listbox = vSelectList(pos=Vec2(10,30),size=Vec2(190,470))
##        self.listbox.setListener(self.listSelected)
##        self.listboxForm.add(self.listbox)
##        gui.add(self.listboxForm)
##        self.listboxForm.hide()

        # major gui
        self.win = MainWin(self)
        self.win.ClearDemos()
        self.win.LoadDemos()


    def closeMsgBox(self,button,key,mouse):
        self.msgForm.hide()
        if self.active:
            self.win.show()

    def OnInit(self):
        pass

    def Cleanup(self):
        self.running = False
        if self.panda != None:
            self.panda.Destroy()
            self.setPandaWorld(None)

    def setPandaWorld(self, panda):
        self.panda = panda
        self.win.ClearDemos()
        self.win.LoadDemos()

    def MessageBox(self, title, msg):
        self.msgForm.setTitle(title)
        self.messageLabel.setText(msg)
        self.msgForm.show()
        if self.active:
            self.win.hide()

    def GetListSelector(self, title, listinfo):
        #dlg = ListSelector(self.win, -1, title, listinfo)
        #dlg.CenterOnParent()
        #ret = dlg.ShowModal()
        #return ret==wx.ID_OK, dlg.listbox.GetStringSelection()
        self.MessageBox("Not Implemented", "This feature is not implemented in this mode.\nPlease install wxPython.")


    def ShowSource(self, filename=None, text=None, nosave=False):
        #self.getMainframe().ShowSource(filename,text,nosave)
        self.MessageBox("Not Implemented", "Editor is not implemented in this mode.\nPlease install wxPython.")

    def ShowSceneGraph(self):
        #self.getMainframe().ShowSceneGraph()
        self.MessageBox("Not Implemented", "Scene Graph is not implemented in this mode.\nPlease install wxPython.")
        pass

    def LoadDemos(self):
        self.win.LoadDemos()

    def LoadAttrsPanel(self):
        self.win.LoadAttrsPanel()

    def setFocus(self):
        pass

    def Activate(self):
        self.active = True
        self.win.show()
        if self.first:
            self.MessageBox("How to activate the menu", "Press F12 to activate and deactivate menu.")
            self.first = False

    def Deactivate(self):
        self.active = False
        self.win.hide()
