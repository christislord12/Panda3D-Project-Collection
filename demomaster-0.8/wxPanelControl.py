import math, datetime, os, traceback, sys
import thread,threading,random,inspect
import demobase
#import win32gui, win32con
from    wx.lib import masked
import wx, wx.aui
from pandac.PandaModules import WindowProperties, ShaderGenerator, StringStream, TextureAttrib
#import direct.directbase.DirectStart
#from direct.showbase.DirectObject import DirectObject
from direct.directbase.DirectStart import *
##class vWorld():
##    def __init__(self, parent,title):
##        return
##        self.myWorldHandle = win32gui.FindWindow(None, title)
##        self.win = wx.Window(parent,size=(width, height))
##        win32gui.SetParent(self.myWorldHandle, self.win.GetHandle())
##        self.SetPosition()
##
##    def SetPosition(self):
##        win32gui.MoveWindow(self.myWorldHandle,-4,-30,self.scenewidth+8,self.sceneheight+34,1)

################################################################################
class VecPanel(wx.Panel):
    def __init__(self, parent, size, attVec):
        wx.Panel.__init__(self, parent, size=size)
        maxv = attVec.maxv
        minv = attVec.minv
        self.fInteger = attVec.fInteger
        w = int(math.floor(max(math.log10(max(1,abs(maxv))), math.log10(max(1,abs(minv)))))) + 1
        if minv < 0 or maxv < 0:
            w+=1
        if minv >= maxv:
            w = max(w, 5)
        if self.fInteger:
            fw = 0
        else:
            fw = attVec.precision
        self.scale = pow(10, fw)
        self.precision = fw
        vec = attVec.getValue()
        self.attVec = attVec
        l = attVec.l
        self.fields = []
        box = wx.FlexGridSizer(0,3,0,0)
        for i in range(l):
            field = masked.Ctrl( self, value=vec[i], integerWidth=w,
                        fractionWidth=fw, size=(30,-1), controlType=masked.controlTypes.NUMBER )
            if minv < maxv:
                slider = wx.Slider(self, minValue = minv * self.scale, maxValue = maxv * self.scale,
                            value=vec[i] * self.scale, size=(70,-1))
                slider.field = field
                field.slider = slider
                slider.Bind(wx.EVT_SLIDER, self.sliderHandler)
            else:
                slider = wx.StaticText(self, label="", size=(70,-1))
            self.fields.append(field)
            box.Add(wx.StaticText(self, label="%d" % (i+1)))
            box.Add(slider)
            box.Add(field)
            field.Bind(wx.EVT_TEXT, self.fieldHandler)
            field.object = attVec.vec[i]
        self.SetSizerAndFit (box)

    def fieldHandler(self, evt):
        field = evt.GetEventObject()
        v = field.GetValue()
        if hasattr(field,'object'):
            field.object.update(v)
        if hasattr(field,'slider'):
            if self.fInteger:
                field.slider.SetValue(int(v))
            else:
                field.slider.SetValue(float(v) * self.scale)

    def CopyToClipboard(self, evt):
        cb = wx.Clipboard()
        if cb.Open():
            self.cb = cb
            info = "("
            for i in range(self.attVec.l):
                field = self.fields[i]
                v = field.GetValue()
                info += ("%%0.%df," % (self.precision)) % v
            info = info[:-1] + ")"
            cb.SetData(wx.TextDataObject(info))
            cb.Close()

    def Reset(self, evt):
        vec = self.attVec.default
        for i in range(self.attVec.l):
            v = vec[i]
            field = self.fields[i]
            v = ("%%0.%df" % (self.precision)) % v
            field.ChangeValue(v)
            if self.fInteger:
                field.slider.SetValue(int(v))
            else:
                field.slider.SetValue(float(v) * self.scale)
        self.attVec.setValue(vec)
        self.attVec.update(self.attVec)

    def sliderHandler(self, evt):
        slider = evt.GetEventObject()
        v = slider.GetValue()
        v = str(v)
        if not self.fInteger:
            v = float(v) / self.scale
            v = ("%%0.%df" % (self.precision)) % v
        slider.field.ChangeValue(v)
        if hasattr(slider.field,'object'):
            slider.field.object.update(v)

class RangePanel(wx.Panel):
    def __init__(self, parent, size, object, label=None):
        wx.Panel.__init__(self, parent, size=size)
        self.object = object
        self.fInteger = object.fInteger
        maxv = object.maxv
        minv = object.minv
        w = int(math.floor(max(math.log10(max(1,abs(maxv))), math.log10(max(1,abs(minv))))))+1
        if minv < 0 or maxv < 0:
            w+=1
        if self.fInteger:
            fw = 0
            # seems a bug in the control, better increase the width
            w+=1
        else:
            fw = object.precision
        if object.minv >= object.maxv:
            w = max(w,5)
        self.field = masked.Ctrl( self, value=object.v, integerWidth=w,
                        fractionWidth=fw, size=(30,-1), controlType=masked.controlTypes.NUMBER )
        if object.minv < object.maxv:
            if self.fInteger:
                self.slider = wx.Slider(self, minValue = object.minv, maxValue = object.maxv, value=object.v,size=(80,-1))
            else:
                self.scale = pow(10, fw)
                self.slider = wx.Slider(self, minValue = object.minv * self.scale, maxValue = object.maxv * self.scale,
                            value=object.v * self.scale, size=(80,-1))
            self.slider.Bind(wx.EVT_SLIDER, self.sliderHandler)
            self.field.slider = self.slider
        else:
            self.slider = wx.StaticText(self, label="",size=(50,-1))
        #if label == None:
        #    label = object.name
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.slider,wx.RIGHT | wx.LEFT ,5)
        box.Add(self.field)
        self.SetSizerAndFit (box)

        self.field.Bind(wx.EVT_TEXT, self.fieldHandler)

    def Reset(self, evt):
        v = self.object.default
        v = str(v)
        if not self.fInteger:
            v = float(v)
            v = ("%%0.%df" % (self.object.precision)) % v
        self.field.ChangeValue(v)
        if self.fInteger:
            self.slider.SetValue(int(v))
        else:
            self.slider.SetValue(float(v) * self.scale)
        #self.object.update(self.defaultValue)
        self.object.update(v)

    def fieldHandler(self, evt):
        v = self.field.GetValue()
        if hasattr(self.field,'slider'):
            if self.fInteger:
                self.slider.SetValue(int(v))
            else:
                self.slider.SetValue(float(v) * self.scale)
        if hasattr(self,'object'):
            self.object.update(v)


    def sliderHandler(self, evt):
        v = self.slider.GetValue()
        v = str(v)
        if not self.fInteger:
            v = float(v) / self.scale
            v = ("%%0.%df" % (self.object.precision)) % v
        self.field.ChangeValue(v)
        if hasattr(self,'object'):
            self.object.update(v)


def FindOrCreateTreeNode(tree, nodename, fromnode, sepmark=":"):
    sep = nodename.find(sepmark)
    if sep >= 0:
        rootname = nodename[0:sep]
        nodename = nodename[sep+1:]
        item, cookie = tree.GetFirstChild(fromnode)
        #print nodename,rootname,item
        while item.IsOk():
              if tree.GetItemText(item) == rootname:
                  return FindOrCreateTreeNode(tree, nodename, item, sepmark)
              item, cookie = tree.GetNextChild(item, cookie)
        # node not exists
        #print "Appending", rootname
        root = tree.AppendItem(fromnode, rootname)
        return FindOrCreateTreeNode(tree, nodename, root, sepmark)
    else:
        #print "Appending", nodename
        item = tree.AppendItem(fromnode, nodename)
        return item

############################################################################################
CMD_IDLE = 10001
CMD_RECOMPILE = 10002
class ControlPanel(wx.Panel):
    def __init__(self, parent, id, log, style, sizehint,panda=None, fPanelHold=False):
        wx.Panel.__init__(self, parent, id, style=style, size=sizehint)
        self.parent = parent
        self.log = log
        self.panda = panda
        if fPanelHold:
            mother = self
            size1 = 210
            size2 = size1 / 2
        else:
            mother = parent
            size1 = 210
            size2 = size1

        f1 = wx.ALL | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT
        box0 = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, CMD_IDLE, "Idle")
        btn.Bind(wx.EVT_BUTTON, self.command)
        box0.Add(btn, f1, 0)
        btn = wx.Button(self, CMD_RECOMPILE, "Recompile")
        btn.Bind(wx.EVT_BUTTON, self.command)
        box0.Add(btn, f1, 0)

        box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.wxListDemos = wx.ListBox(mother,size=(size2,100))
        self.wxListDemos.Bind(wx.EVT_LISTBOX, self.selectListDemos)
        if fPanelHold:
            box1.Add(self.wxListDemos, 0)
        self.wxListDemoFunctions = wx.ListBox(mother,size=(size2,100))#,pos=(100,0))
        self.wxListDemoFunctions.Bind(wx.EVT_LISTBOX, self.selectListDemoFunctions)
        self.wxListDemoBasics = wx.ListBox(mother,size=(size2,100))#,pos=(100,0))
        self.wxListDemoBasics.Bind(wx.EVT_LISTBOX, self.selectListDemoBasics)
        if fPanelHold:
            box1.Add(self.wxListDemoFunctions, 0, f1,0)
            box1.Add(self.wxListDemoBasics, 0, f1,0)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.wxTreeAttrs = wx.TreeCtrl(mother,size=(size1,150))
        self.wxTreeAttrs.Bind(wx.EVT_TREE_SEL_CHANGED, self.selectTreeAttrs)
        if fPanelHold:
            box2.Add(self.wxTreeAttrs, 0, f1, 0)

        self.wxAttPanel = wx.Panel(mother,size=(size1,350))

        if fPanelHold:
            box = wx.BoxSizer(wx.VERTICAL)
            box.Add(box0, 0, wx.EXPAND)
            box.Add(box1, 0, wx.EXPAND)
            box.Add(box2, 0, wx.EXPAND)
            box.Add(self.wxAttPanel, 0, wx.EXPAND)

            self.SetSizerAndFit (box)
        else:
            self.SetSizerAndFit (box0)

        self.LoadDemos()

    def ClearDemos(self):
        self.wxListDemos.Clear()
        self.SelectDemo(-1)

    def LoadDemos(self):
        self.currentdemo = -1
        if self.panda != None:
            for demoinfo in self.panda.demolist:
                path,mod,demo,title,info = demoinfo
                self.wxListDemos.Append(title)
            #self.wxListDemos.SetSelection(0, True)
            self.SelectDemo(-1)

    def command(self, evt):
        self.panda.ClientAcquire()
        try:
            id = evt.GetId()
            if id == CMD_RECOMPILE:
                self.ClearDemos()
                self.panda.recompile()
##                    if not ok:
##                         wx.MessageBox(msg, "Compile error", parent=self)
##                    else:
##                        self.LoadDemos()
            elif id == CMD_IDLE:
                self.SelectDemo(-1)
        except:
            traceback.print_exc(file=sys.stdout)
        self.panda.ClientRelease()

    def LoadAttrsPanel(self):
        #self.wxListAttrs.Clear()
        self.wxTreeAttrs.DeleteAllItems()
        ## TEMP
        #return
        members = inspect.getmembers(self.demo)
        self.attribes = []
        #print members
        treeRoot = self.wxTreeAttrs.AddRoot("All")
        #appRoot = self.wxTreeAttrs.AppendItem(treeRoot, "App")
        for pair in members:
            name,value = pair
            if name.find("att_") == 0 and value != None:
                #self.attribes.append(value)
                #self.wxListAttrs.Append(name[4:])
                nodename = value.getNodeName()
                sep = nodename.find(":")

                if sep <= 0:
                    nodename = "App:" + nodename
                item = FindOrCreateTreeNode(self.wxTreeAttrs, nodename, treeRoot, ":")
                #self.wxTreeAttrs.SetItemData(item,wx.TreeItemData(value))
                # store the name of the member instead of the value
                self.wxTreeAttrs.SetItemData(item,wx.TreeItemData(name))

##                if sep >= 0:
##                    rootname = nodename[0:sep]
##                    item = appRoot
##                    root = None
##                    while item.IsOk():
##                        item = self.wxTreeAttrs.GetNextSibling(item)
##                        if item.IsOk() and self.wxTreeAttrs.GetItemText(item) == rootname:
##                            root = item
##                            break
##                    if root == None:
##                        root = self.wxTreeAttrs.AppendItem(treeRoot, rootname)
##                    nodename = nodename[sep+1:]
##                else:
##                    root = appRoot
##                self.wxTreeAttrs.AppendItem(root, nodename, data=wx.TreeItemData(value))
        self.wxTreeAttrs.ExpandAll()
        self.wxTreeAttrs.EnsureVisible(treeRoot) #appRoot)

    def SelectDemo(self, i):
        if i >= 0:
            if i != self.currentdemo:
                self.wxListDemoFunctions.Clear()
                self.wxListDemoBasics.Clear()
                demoinfo = self.panda.demolist[i]
                path,mod,demo,title,info = demoinfo
                self.demo = demo
                nr = 0
                #self.wxListDemoFunctions.Append("Information")
                self.basics = 0
                for entry in demo.entries:
                    entryname, entryfunction, desc = entry
                    if entryname.find("_base") == 0:
                        self.basics += 1
                        self.wxListDemoBasics.Append("%d. %s" % (self.basics, desc))
                    else:
                        nr += 1
                        self.wxListDemoFunctions.Append("%d. %s" % (nr, desc))
                self.panda.InitDemo(demoinfo)
                self.ClearAttrDetailPanel()
                # the init demo call is delayed, so it has to be called later
                # self.LoadAttrsPanel()
                self.currentdemo = i
        else:
            self.wxListDemos.SetSelection(-1)
            if self.panda != None:
                self.panda.InitDemo(None)
            self.wxListDemoFunctions.Clear()
            self.wxListDemoBasics.Clear()
            self.wxTreeAttrs.DeleteAllItems()
            self.currentdemo = i
            self.ClearAttrDetailPanel()


    def selectListDemos(self, evt):
        i = self.wxListDemos.GetSelection()
        self.SelectDemo(i)


    def CreateControlFromAttr(self, attribe, box, row):
        if hasattr(attribe, 'name'):
            name = attribe.name
            i = name.rfind(":")
            if i >= 0:
                name = name[i+1:]

        if attribe.__class__  == demobase.Att_Boolean:
            checkbox = wx.CheckBox(self.wxAttPanel,size=(30,-1))
            checkbox.SetValue(attribe.v)
            checkbox.Bind(wx.EVT_CHECKBOX, self.checkboxHandler)
            checkbox.object = attribe
            box.Add(checkbox, wx.GBPosition(row,0))
            box.Add(wx.StaticText(self.wxAttPanel, label=name), wx.GBPosition(row,1), wx.GBSpan(1,2))
            return row+1

        if attribe.__class__  in [ demobase.Att_IntRange, demobase.Att_FloatRange]:
            box.Add(wx.StaticText(self.wxAttPanel, label=name), wx.GBPosition(row,0), wx.GBSpan(1,1))
            btn = wx.Button(self.wxAttPanel,-1,"Reset",size=(-1,15))
            box.Add(btn, wx.GBPosition(row,1), wx.GBSpan(1,2))
            row += 1
            ranger = RangePanel(self.wxAttPanel, (200,-1), attribe)
            box.Add(ranger, wx.GBPosition(row,1), wx.GBSpan(1,2))
            btn.Bind(wx.EVT_BUTTON, ranger.Reset)
            return row+1

        if attribe.__class__ == demobase.Att_color:
            box.Add(wx.StaticText(self.wxAttPanel, label=name), wx.GBPosition(row,0), wx.GBSpan(1,3))
            row += 1
            cp = wx.ColourPickerCtrl(self.wxAttPanel, col=attribe.getRGBColor(), style=wx.CLRP_SHOW_LABEL)
            cp.Bind(wx.EVT_COLOURPICKER_CHANGED, self.colorPickHandler)
            cp.object = attribe
            box.Add(cp, wx.GBPosition(row,1), wx.GBSpan(1,2))
            return row+1

        if attribe.__class__ == demobase.Att_Vecs:
            box.Add(wx.StaticText(self.wxAttPanel, label=name), wx.GBPosition(row,0), wx.GBSpan(1,1))
            btnR = wx.Button(self.wxAttPanel,-1,"Reset",size=(-1,15))
            box.Add(btnR, wx.GBPosition(row,1), wx.GBSpan(1,1))
            btnC = wx.Button(self.wxAttPanel,-1,"Copy",size=(-1,15))
            box.Add(btnC, wx.GBPosition(row,2), wx.GBSpan(1,1))
            row+=1
            vec = VecPanel(self.wxAttPanel, (180,-1), attribe)
            box.Add(vec, wx.GBPosition(row,1), wx.GBSpan(1,2))
            btnR.Bind(wx.EVT_BUTTON, vec.Reset)
            btnC.Bind(wx.EVT_BUTTON, vec.CopyToClipboard)
            return row+1

        # screen if att_ attribute exists
        members = inspect.getmembers(attribe)
        for pair in members:
            name,value = pair
            if name.find("att_") == 0:
                row = self.CreateControlFromAttr(value, box, row)
        return row

    def ClearAttrDetailPanel(self):
        # clear the panel first
        sizer = self.wxAttPanel.GetSizer()
        box = wx.BoxSizer()
        self.wxAttPanel.SetSizerAndFit(box)
        self.wxAttPanel.DestroyChildren()

    def selectTreeAttrs(self, evt):
        parent = self.wxAttPanel.GetParent()
        fScrolled = isinstance(parent, wx.ScrolledWindow)

        if fScrolled:
            parent.Scroll(0,0)

        self.ClearAttrDetailPanel()
        item = self.wxTreeAttrs.GetSelection()
        #self.wxTreeAttrs.SetItemImage(item, 0)
        #attribe = self.wxTreeAttrs.GetItemData(item).GetData()
        attribename = self.wxTreeAttrs.GetItemData(item).GetData()
        if attribename == None:
            attribe = None
        else:
            attribe = getattr(self.demo, attribename)
        #box = wx.FlexGridSizer(0,2,0,0)
        #box.Add(wx.StaticText(self.wxAttPanel, label="Attribe", size=(50,-1)), 0, wx.TOP + wx.BOTTOM, 5)
        #box.Add(wx.StaticText(self.wxAttPanel, label="Value"), 0, wx.TOP + wx.BOTTOM, 5)

        #if attribe == None:
        #    box.Add(wx.StaticText(self.wxAttPanel, label="None"))
        #else:
        #    self.CreateControlFromAttr(attribe, box)

        box = wx.GridBagSizer(0,0)
        if attribe == None:
            box.Add(wx.StaticText(self.wxAttPanel, label="None"), wx.GBPosition(0,0))
        else:
            self.CreateControlFromAttr(attribe, box, 0)


        self.wxAttPanel.SetSizerAndFit(box)

        if fScrolled:
            w,h = box.GetSize()
            parent.SetScrollbars(20, 20, (w+19)/20, (h+19)/20+1);

    def selectListDemoFunctions(self, evt):
        j = self.wxListDemoFunctions.GetSelection()
        self.executeFunction(j, False)
        self.wxListDemoFunctions.SetSelection(-1)

    def selectListDemoBasics(self, evt):
        j = self.wxListDemoBasics.GetSelection()
        self.executeFunction(j, True)

    def executeFunction(self, j, basics):
        if self.panda != None:
            if not basics:
                j += self.basics

            if True:
                i = self.wxListDemos.GetSelection()
                self.panda.ClientAcquire()
                demoinfo = self.panda.demolist[i]
                path,mod,demo,title,info = demoinfo
                entryname, entryfunction, doc = demo.entries[j]
                try:
                    #print "entry"
                    entryfunction()
                except:
                    traceback.print_exc(file=sys.stdout)

                # give focus to panda window if it is not basic functions
                #if entryname.find("_base") != 0:
                if not basics:
                    self.parent.p3dSurfaceFocus()
                self.panda.ClientRelease()

    def colorPickHandler(self, evt):
        colorpicker = evt.GetEventObject()
        if hasattr(colorpicker,'object'):
            color = colorpicker.GetColour()
            colorpicker.object.setRGBColor(color)

    def checkboxHandler(self, evt):
        checkbox = evt.GetEventObject()
        if hasattr(checkbox,'object'):
            v = checkbox.GetValue()
            checkbox.object.update(v)

    def setPandaWorld(self, panda):
        self.panda = panda
        self.ClearDemos()
        self.LoadDemos()



###################################################################
class SceneGraphPanel(wx.Panel):
    def __init__(self, parent, id, panda):
        wx.Panel.__init__(self, parent, id)
        self.panda = panda
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        boxleft = wx.BoxSizer(wx.VERTICAL)
        btn = wx.Button(self, -1, "Reload")
        btn.Bind(wx.EVT_BUTTON, self.reload)
        boxleft.Add(btn)

        self.wxTreeGraph = wx.TreeCtrl(self,size=(350,500))
        self.wxTreeGraph.Bind(wx.EVT_TREE_SEL_CHANGED, self.selectTreeGraph)
        boxleft.Add(self.wxTreeGraph)

        sizer.Add(boxleft,0,wx.EXPAND)

        boxright = wx.BoxSizer(wx.VERTICAL)
        self.tcInfo = wx.TextCtrl(self, style = wx.TE_MULTILINE, size=(400, 500))
        boxright.Add(self.tcInfo)
        sizer.Add(boxright,0,wx.EXPAND)

        self.SetSizer(sizer)

        self.reload(None)
        #render.ls()

    def selectTreeGraph(self, evt):
        item = self.wxTreeGraph.GetSelection()
        treepath = self.wxTreeGraph.GetItemData(item).GetData()
        if treepath == None:
            return
        np = self._getNodePathFromTreePath(treepath)
        if np != None:
            name,pandanodename,itemname = self._getNodePathItemName(np)
            #print itemname
            #print self.wxTreeGraph.GetItemText(item)
            if itemname == self.wxTreeGraph.GetItemText(item):
                # match
                self._loadNodePath(np,pandanodename)
                return
        self.reload(None)

    def _getNodePathInfo(self, np):
        pos = np.getPos()
        hpr = np.getHpr()
        return "NodePath\n\tPosition: (%0.1f, %0.1f, %0.1f)\n\tHPR: (%0.1f, %0.1f, %0.1f)\n\n" % (pos[0],pos[1],pos[2],hpr[0],hpr[1],hpr[2])

    def _getCameraInfo(self, camnode):
        lens = camnode.getLens()
        far = lens.getFar()
        near = lens.getNear()
        fov = lens.getFov()
        return "Camera:\n\tNear: %0.f\n\tFar: %0.f\n\tFov:(%0.1f, %0.1f)\n" % (near,far,fov[0],fov[1])

    def _getGeomNodeInfo(self, np, geomnode):
        nrgeoms = geomnode.getNumGeoms()

        ss = StringStream()
        gs = geomnode.getGeomState(0)
        gs.output(ss)
        state = ss.getData()

        rs = np.getNetState()
        newrs = rs.compose(gs)

        ss = StringStream()
        newrs.output(ss)
        state1 = ss.getData()

        sg = ShaderGenerator.getDefault()
        shader = sg.synthesizeShader(newrs).getShader()
        text=shader.getText()

        return "GeomNode:\n\nNumber of geoms: %d\n\nGeom State 0: %s\n\nNet State for Geom 0:\n%s\nShader (auto):\n%s\n" % (nrgeoms,state, newrs, text)

    def _loadNodePath(self, np, pandanodename):
        self.tcInfo.Clear()
        info = self._getNodePathInfo(np)

        ss = StringStream()
        rs = np.getNetState()
        rs.output(ss)
        info += "Render Net State: %s\n\n" % ss.getData()

        ss = StringStream()
        rs = np.getState()
        rs.output(ss)
        info += "Render State: %s\n\n" % ss.getData()

##        ta = np.getAttrib(TextureAttrib.getClassType())
##        if ta != None:
##            info += "TextureAttrib defined\n"
##        else:
##            info += "TextureAttrib not defined\n"
##
##        tex = np.hasTexture()
##        if tex:
##            info += "Has Texture\n"
##        else:
##            info += "No Texture\n"

##        shader = np.getShader()
##        if shader != None:
##            text = shader.getText()
##            info += "Shader\n%s\n" % text

        if pandanodename == "Camera":
            info += self._getCameraInfo(np.node())
        elif pandanodename == "GeomNode":
            info += self._getGeomNodeInfo(np, np.node())

        self.tcInfo.SetValue(info)

    def _getNodePathFromTreePath(self, treepath):
        # walk the tree to see if the scene graph match the current screen
        root = [render, render2d]
        np = root[treepath[0]]
        for i in range(1, len(treepath)):
            if treepath[i] >= np.getNumChildren():
                return None
            np = np.getChild(treepath[i])
        return np

    def reload(self, evt):
        self.wxTreeGraph.DeleteAllItems()
        treeRoot = self.wxTreeGraph.AddRoot("All")
        i = 0
        for np in [render, render2d]:
            self._loadNode(treeRoot, np, [i])
            i+=1

        self.wxTreeGraph.Expand(treeRoot)
        #self.wxTreeGraph.ExpandAllChildren(treeRoot)
        self.wxTreeGraph.EnsureVisible(treeRoot) #appRoot)

    def _getNodePathItemName(self, np):
        name = np.getName()
        pandanode = np.node()
        pandanodename = "%s" % pandanode.__class__
        e = pandanodename.rfind("'")
        b = pandanodename.rfind(".")
        pandanodename = pandanodename[b+1:e]
        itemname = '%s "%s"' % (pandanodename,name)
        return name,pandanodename, itemname

    def _loadNode(self, rootTnode, np, treepath):
        name,pandanodename,itemname = self._getNodePathItemName(np)
        newTnode = self.wxTreeGraph.AppendItem(rootTnode, itemname)
        self.wxTreeGraph.SetItemData(newTnode,wx.TreeItemData(treepath))
        childs = np.getNumChildren()
        for i in range(childs):
            newtreepath = treepath + [i]
            self._loadNode(newTnode, np.getChild(i), newtreepath)
        if len(treepath) < 2:
            #self.wxTreeGraph.ExpandAllChildren(newTnode)
            self.wxTreeGraph.Expand(newTnode)
            pass
        else:
            self.wxTreeGraph.CollapseAllChildren(newTnode)

