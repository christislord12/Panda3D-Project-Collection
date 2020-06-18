import math, datetime, os, traceback, sys
import wxPanelControl
import thread,threading,random,inspect
#import demobase
#import win32gui, win32con
from    wx.lib import masked
import wx, wx.aui, mupued
from pandac.PandaModules import WindowProperties
#import direct.directbase.DirectStart
#from direct.showbase.DirectObject import DirectObject
#from direct.directbase.DirectStart import *

################################################################################
class JobThreadBase():
    def __init__(self, log):
        #self.parent = parent
        self.log = log
        self.keepGoing = self.running = False
        self.lock = threading.Semaphore()

    def __del__(self):
        self.StopAndWait()

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def StopAndWait(self):
        self.Stop()
        while (self.running):
            time.sleep(0.01)

    def IsRunning(self):
        return self.running

    def IsKeepGoing(self):
        return self.keepGoing

#######################################################################################
# this is the frame to hold scene graph, editors, message window
# note that it is not created by default
class MainFrame(wx.Frame):
    SCENE_GRAPH = 10001
    NEW_FILE = 10002
    CLOSE_WINDOW =10003
    def __init__(self, title, pos, size, panda):
        wx.Frame.__init__(self, None, -1, title, pos, size=size)
        self.panda = panda
        sizer = wx.BoxSizer(wx.VERTICAL)
        f1 = wx.ALL | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT
        box = wx.BoxSizer(wx.HORIZONTAL)
        btns = [
            (self.SCENE_GRAPH, "Scene Graph"),
            (self.NEW_FILE, "New File"),
            (self.CLOSE_WINDOW, "Close")
        ]
        for btninfo in btns:
            btn = wx.Button(self,id=btninfo[0],label=btninfo[1])
            btn.Bind(wx.EVT_BUTTON, self.btnevent)
            box.Add(btn, 0, f1, 0)
        self.nb = wx.Notebook(self, style=wx.CLIP_CHILDREN, size=(790,550))
        sizer.Add(box, 0, wx.EXPAND)
        sizer.Add(self.nb, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.SetSizeHints(self)

        #self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, ...)

    def btnevent(self, evt):
        id = evt.GetId()
        if id == self.NEW_FILE:
            newwin = self.ShowSource("New")
            filename = newwin.filename
            if filename != None:
                sep = filename.rfind(os.sep)
                if sep < 0:
                    title = filename
                else:
                    title = filename[sep+1:]
                self.nb.SetPageText(self.nb.GetSelection(), title)
        elif id == self.CLOSE_WINDOW:
            page = self.nb.GetSelection()
            if page >= 0:
                self.nb.DeletePage(page)
        elif id == self.SCENE_GRAPH:
            self.ShowSceneGraph()

    def ShowSceneGraph(self):
        win=wxPanelControl.SceneGraphPanel(self.nb, -1, self.panda)
        self.nb.AddPage(win, "Scene Graph", True)
        return win

    def ShowSource(self, filename=None, text=None, nosave=False):
        #win=mupued.mupuEdAlone(None, title="Source Code", pos=(100,250), size=(700,500))
        win=mupued.mupuEdChild(self.nb)
        if filename == None:
            title = "Information"
        else:
            sep = filename.rfind(os.sep)
            if sep < 0:
                title = filename
            else:
                title = filename[sep+1:]
        self.nb.AddPage(win, title, True)
        win.nosave = nosave
        if filename != None:
            win.loadFile(filename)
        else:
            win.SetText(text)
        return win

##    def addPage(self, subtitle, win):
##        win.Reparent(self.nb1)
##        self.nb.AddPage(win, subtitle)

# this is the control panel
class ControlWindow(wx.Frame):
    def __init__(self, title, pos, size, panda, docking):
        self.panda = panda
        self.docking = docking

        wx.Frame.__init__(self, None, -1, title, pos, size=size)
        if self.docking:
            self.setDocking()

        self.setupWindows()

    def setupWindows(self):
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(self)

        self.topPanel = wxPanelControl.ControlPanel(self, -1, self, sizehint=(224,20), style=wx.SIMPLE_BORDER, panda = self.panda)
        w = 215
        self.mgr.AddPane(self.topPanel, wx.aui.AuiPaneInfo().
              Name("button").
              Caption("Buttons").
              CaptionVisible(False).
              Fixed().
              Left().
              Layer(1).
              Position(1).
              #MinSize(wx.Size(224,10)).
              BestSize(wx.Size(210,26)).
              CloseButton(False).
              MaximizeButton(False)
            )
        self.mgr.AddPane(self.topPanel.wxListDemos, wx.aui.AuiPaneInfo().
              Name("application").
              Caption("Applications").
              Fixed().
              Left().
              Layer(1).
              Position(2).
              #MinSize(wx.Size(224,100)).
              BestSize(wx.Size(w,120)).
              CloseButton(False).
              MaximizeButton(False)
            )

        self.nb1 = wx.Notebook(self, style=wx.CLIP_CHILDREN)
        self.topPanel.wxListDemoFunctions.Reparent(self.nb1)
        self.nb1.AddPage(self.topPanel.wxListDemoFunctions, "Functions")
        self.topPanel.wxListDemoBasics.Reparent(self.nb1)
        self.nb1.AddPage(self.topPanel.wxListDemoBasics, "Basics")
        self.topPanel.wxTreeAttrs.Reparent(self.nb1)
        self.nb1.AddPage(self.topPanel.wxTreeAttrs, "Attributes")

        self.mgr.AddPane(self.nb1, wx.aui.AuiPaneInfo().
              Name("Mid").
              Caption(("Mid")).
              CaptionVisible(False).
              Fixed().
              Left().
              Layer(1).
              Position(3).
              Fixed().
              MinSize(wx.Size(w,100)).
              BestSize(wx.Size(w,120)).
              CloseButton(False).
              MaximizeButton(False)
            )

        self.log = wx.TextCtrl(self, -1,
                              style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        self.nb2 = wx.Notebook(self, style=wx.CLIP_CHILDREN)
        sw = wx.ScrolledWindow(self.nb2)
        sw.SetScrollbars(20, 20, 50, 50);
        self.topPanel.wxAttPanel.Reparent(sw)
        self.nb2.AddPage(sw, "Attributes")
        self.log.Reparent(self.nb2)
        self.nb2.AddPage(self.log, "Messages")

        self.mgr.AddPane(self.nb2, wx.aui.AuiPaneInfo().
              Name("Low").
              Caption(("Low")).
              CaptionVisible(False).
              Left().
              Layer(1).
              Fixed().
              Position(4).
              MinSize(wx.Size(w,100)).
              BestSize(wx.Size(w,200)).
              CloseButton(False).
              MaximizeButton(False)
            )

##        self.kwfilter = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)
##        self.kwfilter.ShowCancelButton(True)
##        self.mgr.AddPane(self.kwfilter, wx.aui.AuiPaneInfo().
##          Name("filter").
##          Caption(("SEARCH")).
##          Left().
##          Layer(1).
##          Position(2).
##          BestSize(wx.Size(-1,26)).
##          Fixed().
##          CloseButton(False).
##          MaximizeButton(False)
##        )

        if self.docking:
            self.mainLB = guiMainListbook.createMainLB(self, self, self.log)
            self.mainLB.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNbtabClick)
            self.surf = self.mainLB.panels[0]

            #self.mainLB = wx.Panel(self, size=(800,600))
            #self.mainLB = wx.Window(self, size=(800,600))
            #self.surf = self.mainLB

            self.mgr.AddPane(self.mainLB, wx.aui.AuiPaneInfo().CenterPane().Name("mainPanel"))

##        self.mgr.AddPane(self.log,
##                         wx.aui.AuiPaneInfo().
##                         Bottom().BestSize((-1, 80)).
##                         MinSize((-1, 10)).
##                         Floatable(wxMainApp.ALLOW_AUI_FLOATING).FloatingSize((500, 160)).
##                         Caption("Messages").
##                         CloseButton(False).
##                         Name("LogWindow"))

        self.mgr.Update()
        self.p3dSurfaceFocus()

    def OnNbtabClick(self, evt):
        #print "Selected", evt.GetSelection()
        if evt.GetSelection() == 0:
            wp = WindowProperties()
            wp.setForeground(True)
            base.win.requestProperties(wp)
            self.surf.SetFocus()
            self.p3dSurfaceFocus()
        else:
            wp = WindowProperties()
            wp.setForeground(False)
            base.win.requestProperties(wp)
        evt.Skip()

    def p3dSurfaceFocus(self):
        if not self.docking:
            wp = WindowProperties()
            wp.setForeground(True)
            base.win.requestProperties(wp)
            return

        import win32gui
        myWorldHandle = win32gui.FindWindowEx(self.surf.GetHandle(), 0, None, "Panda")
        if myWorldHandle != 0:
            win32gui.SetFocus(myWorldHandle)
        return
        # wx.Window_FromHWND
##        wp = WindowProperties()
##        wp.setForeground(True)
##        base.win.requestProperties(wp)
##        return
##
##        if hasattr(self, "wp"):
##            self.wp.setForeground(True)
##            print self.wp.getTitle()
##        return
##
##        import win32gui
##        print self.surf.GetHandle()
##        self.myWorldHandle = win32gui.FindWindowEx(self.surf.GetHandle(), 0, None, "Panda")
##        print self.myWorldHandle
##        if self.myWorldHandle != 0:
##            win32gui.SetFocus(self.myWorldHandle)
##        return
##        #print self.surf.GetHandle()
##        w = wx.FindWindowByName("Panda", self.surf)
##        print w
##        return
##        w = self.surf.GetChildren()
##        print w
##        if len(w) > 0:
##            w[0].SetFocus()
##        #self.surf.SetFocus()
##        wp = WindowProperties()
##        wp.setForeground(True)
##        base.win.requestProperties(wp)
##        print "setting foregr"

    def setDocking(self):
        '''P3D surface initializations'''
        wp = WindowProperties().getDefault()
        wp.setOrigin(0,0)
        wp.setSize(800, 600)
        wp.setParentWindow(self.surf.GetHandle())
        self.wp = wp

        return base.openDefaultWindow(props=wp)

    def setPandaWorld(self, panda):
        self.panda = panda
        self.topPanel.setPandaWorld(panda)

    #def Destroy(self):
        #self.panda.Destroy()
        #wxMainApp.wxstMainFrame.Destroy(self)
        #sys.exit()

class ListSelector(wx.Dialog):
    def __init__(self, parent, ID, title, listinfo, pos=wx.DefaultPosition, size=wx.DefaultSize,style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)

        box = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self, style=wx.LB_SORT)
        for s in listinfo:
            self.listbox.Append(s)
        box.Add(self.listbox, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER|wx.ALL, 2)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        btnOK = wx.Button(self, wx.ID_OK, "OK")
        btnOK.SetDefault()
        btnCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        hbox.Add(btnOK, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5)
        hbox.Add(btnCancel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5)
        box.Add(hbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER|wx.ALL, 2)
        self.SetSizer(box)
        box.Fit(self)

class myApp(wx.App):
    WIDTH = 1024
    HEIGHT = 740
    NODOCKWIDTH = 224
    MAINFRAME_HEIGHT=600
    def __init__(self, panda=None):
        self.panda = panda
        wx.App.__init__(self, 0)
        self.running = True

    def OnInit(self):
        self.evtLoop = wx.EventLoop()
        self.oldLoop = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(self.evtLoop)

        self.docking = False # docking seems have problem in panda with the default mouse driver
        if not self.docking:
            pos = (self.WIDTH-self.NODOCKWIDTH,0)
            size=(self.NODOCKWIDTH,self.HEIGHT)
        else:
            pos = (0,0)
            size = wx.Size(self.WIDTH, self.HEIGHT)
        self.win = ControlWindow("Master Control", pos, size, self.panda, docking=self.docking)
        self.SetTopWindow(self.win)
        #self.win.CenterOnScreen()
        self.win.Show(True)
        self.win.Bind(wx.EVT_CLOSE, self.onClose)
        self.mainframe = None
        #print "main loop is running" , self.IsMainLoopRunning()
        return True

    def getMainframe(self):
        if self.docking:
            return self.win
        if self.mainframe != None:
            return self.mainframe
        self.mainframe = MainFrame("Master Information Window",(0,self.HEIGHT-self.MAINFRAME_HEIGHT), (self.WIDTH-self.NODOCKWIDTH, self.MAINFRAME_HEIGHT), self.panda)
        self.SetTopWindow(self.mainframe)
        self.mainframe.Show(True)
        self.mainframe.Bind(wx.EVT_CLOSE, self.onMainframeClose)
        return self.mainframe

    def onMainframeClose(self, event):
        self.mainframe.Destroy()
        self.mainframe = None

    def Cleanup(self):
        self.running = False
        if self.panda != None:
            self.panda.Destroy()
            self.setPandaWorld(None)
#        self.win.SaveOnClose()
        self.win.Destroy()
        if self.mainframe != None:
            self.mainframe.Destroy()

    def onClose(self, event):
        self.Cleanup()
        #while self.evtLoop.Pending(): self.evtLoop.Dispatch()
        try: base.userExit()
        except: sys.exit()
        sys.exit()
        #base.disableAllAudio()
        #base.closeWindow( base.win )
        #base.userExit()
        #base.shutdown()
        #base.destroy()

    def setPandaWorld(self, panda):
        self.panda = panda
        self.win.setPandaWorld(panda)

    def MessageBox(self, title, msg):
        wx.MessageBox(msg, title)

    def GetListSelector(self, title, listinfo):
        dlg = ListSelector(self.win, -1, title, listinfo)
        dlg.CenterOnParent()
        ret = dlg.ShowModal()
        return ret==wx.ID_OK, dlg.listbox.GetStringSelection()


    def ShowSource(self, filename=None, text=None, nosave=False):
        self.getMainframe().ShowSource(filename,text,nosave)

    def ShowSceneGraph(self):
        self.getMainframe().ShowSceneGraph()


    def LoadDemos(self):
        self.win.topPanel.LoadDemos()

    def LoadAttrsPanel(self):
        self.win.topPanel.LoadAttrsPanel()

    def setFocus(self):
        self.win.p3dSurfaceFocus()

#    def MainLoop(self):
#        print "Mainloop"

class WxMainApp(JobThreadBase):
    def __init__(self, log, panda):
        JobThreadBase.__init__(self,log)
        self.panda = panda

    def Run(self):
        self.app = myApp(self.panda)
        try:
            self.app.MainLoop()
        except:
            traceback.print_stack()
        self.running = False

###########################################3
##ID_ABOUT = 101
##ID_EXIT  = 102
##import wx.aui
##
##class MyFrame(wx.Frame):
##    def __init__(self, parent, ID, title):
##        wx.Frame.__init__(self, parent, ID, title,
##                         wx.DefaultPosition, wx.Size(200, 150))
##        self.CreateStatusBar()
##        self.SetStatusText("This is the statusbar")
##
##        menu = wx.Menu()
##        menu.Append(ID_ABOUT, "&About",
##                    "More information about this program")
##        menu.AppendSeparator()
##        menu.Append(ID_EXIT, "E&xit", "Terminate the program")
##
##        menuBar = wx.MenuBar()
##        menuBar.Append(menu, "&File");
##
##        self.SetMenuBar(menuBar)
##        self.mgr = wx.aui.AuiManager()
##        self.mgr.SetManagedWindow(self)
##        self.panda = None
##        self.topPanel = wxPanelControl.ControlPanel(self, -1, self, sizehint=(224,20), style=wx.SIMPLE_BORDER, panda = self.panda)
##        self.mgr.Update()
##
##class myAppDummy(wx.App):
##
##    WIDTH = 1024
##    HEIGHT = 740
##    def __init__(self, panda=None):
##        self.panda = panda
##        wx.App.__init__(self, 0)
##        self.running = True
##
##    def OnInit(self):
##        frame = MyFrame(None,-1, "Hello from wxPython")
##        frame.Show(True)
##        self.SetTopWindow(frame)
##        return True
##
##    def Cleanup(self):
##        return
##        self.running = False
##        if self.panda != None:
##            self.panda.Destroy()
##            self.setPandaWorld(None)
##        self.win.SaveOnClose()
##        self.win.Destroy()
##
##    def onClose(self, event):
##        self.Cleanup()
##        #while self.evtLoop.Pending(): self.evtLoop.Dispatch()
##        try: base.userExit()
##        except: sys.exit()
##        sys.exit()
##        #base.disableAllAudio()
##        #base.closeWindow( base.win )
##        #base.userExit()
##        #base.shutdown()
##        #base.destroy()
##
##    def setPandaWorld(self, panda):
##        self.panda = panda
##        #self.win.setPandaWorld(panda)
##
###    def MainLoop(self):
###        print "Mainloop"
##
#########################################3

def main():
    _app = myApp()
    _app.MainLoop()

if __name__ == '__main__':
    main()



