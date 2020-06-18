from pandac.PandaModules import loadPrcFileData, ConfigVariableBool
loadPrcFileData("", "framebuffer-multisample #t")
loadPrcFileData("", "multisamples 1") # as much as it can
loadPrcFileData("", "sync-video #t")
#loadPrcFileData("", "want-directtools #t")
#loadPrcFileData("", "want-tk #t")
loadPrcFileData("", "win-size 800 600")
#loadPrcFileData("", "win-size 640 480")
#loadPrcFileData("", "win-size 120 120")
#loadPrcFileData("", "basic-shaders-only #f")
#loadPrcFileData("", "prefer-parasite-buffer #f")
loadPrcFileData("", "textures-power-2 none")

import direct.directbase.DirectStart
from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3, AntialiasAttrib, Mat4
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Filename
from direct.task.Task import Task
from pandac.PandaModules import loadPrcFileData, loadPrcFile
import sys, threading, os, time
#from direct.filter.CommonFilters import CommonFilters
from pandac.PandaModules import ModelPool,ShaderPool,TexturePool #,MaterialPool
from pandac.PandaModules import PandaSystem

import random
#import wxDemoControl
#import odebase
import dynamicimporter
import demobase
import inspect
def preparePaths(path1,path2):
    for p in [ 'model-path', 'sound-path', 'texture-path', 'particle-path', 'shader-path']:
        loadPrcFileData("", "%s %s" % (p,path2))
        loadPrcFileData("", "%s %s" % (p,path1))
        #config = ConfigVariableSearchPath(p)
        #config.clearLocalValue()
        #config.appendPath(path)
        #print config

class Container(DirectObject):
    def __init__(self, fMultithread, demolist, wxApp):
        random.seed()
        #DirectObject.__init__(self)
        base.setBackgroundColor(0.5, 0.5, 0.5)
        major = PandaSystem.getMajorVersion()
        minor = PandaSystem.getMinorVersion()
        #print PandaSystem.getNumSystems()
        self.pandaversion = float(major) + float(minor) / 10

        self.loaddemolist(demolist)
        self.currentdemo = None

        self.fwxControl = (wxApp != None)
        self.guiOn = False
        if wxApp == None:
            import pgDemoControl
            wxApp = pgDemoControl.Controller(self)
            self.accept("f12", self.ToggleGUI)

        self.wxApp = wxApp
        #self.odeworld = odebase.ODEWorld_AutoHash()
        #self.odeworld = odebase.ODEWorld_Simple()
        base.enableParticles()
        base.setFrameRateMeter(True)

        self.fMultithread = fMultithread
        if fMultithread:
            # create two semaphore to allow multi-threaded programs to access
            # the panda objects
            self.entrylock = threading.Semaphore(0)
            self.pandalock =  threading.Semaphore(1)

        self.keys = set()

        self.accept('window-event', self.winEvent)
        base.userExit = lambda: None
        self.fForeground = False
        self.foregroundEventListener = set()
        self.cwd = os.getcwd()
        self.pendingcompile = False

        df = base.camLens.getFov()
        self.saveFov = df[0]

        self.ready = True
        # auto load the first application if only one specified
        if len(demolist) == 1:
            self.InitDemo(self.demolist[0])
        elif not self.fwxControl:
            self.ActivateGUI()

    def loaddemolist(self, demolist):
        self.demolist = []
        for demoinfo in demolist:
            path,mod,c = demoinfo
            demo =  c(self)
            #print path
            title,info = self.getDemoInformation(c)
            self.demolist.append((path,mod,demo,title,info))
        self.demolist.sort(cmp=lambda x,y: cmp(x[3].lower(), y[3].lower()))
        for demoinfo in self.demolist:
            print "%s : [%s]" % (demoinfo[2].__class__.__name__, demoinfo[3])

    def ClearAllModules(self):
        # unload all module one level below the current directory
        l = len(self.cwd)
        unloadlist = []
        for m in sys.modules:
            if hasattr(sys.modules[m], "__file__"):
                unloadthis = False
                filename = sys.modules[m].__file__
                if filename.find(self.cwd) == 0:
                    filename = filename[l:]
                    if len(filename) > 0 and filename[0] != os.sep:
                        unloadthis = True
                elif len(filename) > 1 and filename[1] != ":" and filename[0] != os.sep:
                    unloadthis = True
                if unloadthis:
                    unloadlist.append(m)
        for m in unloadlist:
            del sys.modules[m]

        #for demoinfo in self.demolist:
        #    path,mod,c = demoinfo
        #    del sys.modules[mod.__name__]
        self.demolist = []

    def recompile(self):
        if self.currentdemo != None:
            self.pendingcompile = True
            self.InitDemo(None)
            return

        self.ClearAllModules()
        importer = dynamicimporter.DynamicImporter()
        importer.setRedirect()
        importer.compileAll()
        ok, demolist = importer.ImportCompiledObjects(demobase.DemoBase,None,False)
        importer.restoreRedirect()
        self.loaddemolist(demolist)

        if self.wxApp != None:
            if ok:
                self.wxApp.LoadDemos()
            else:
                self.ShowSource(text=importer.output)

    def getPandaVersion(self):
        return self.pandaversion

    def winEvent(self, win):
        if win == base.winList[0]:
            properties = win.getProperties()
            #print "Got window event: %s" % (repr(properties))
            #print "getOpen = "+str(properties.getOpen())
            if not properties.getOpen():
                #print "User closed main window."
                # it is not a docking mode, use click to quit the app
                wxApp = self.wxApp
                self.Destroy()
                if wxApp != None:
                    wxApp.setPandaWorld(None)
                    wxApp.Cleanup()
                    #while wxApp.evtLoop.Pending(): wxApp.evtLoop.Dispatch()
                sys.exit()
            fForeground = properties.getForeground()
            if self.fForeground != fForeground:
                # focus changed
                self.fForeground = fForeground
                for e in self.foregroundEventListener:
                    e.forgroundEventHandler(fForeground)

    def registerForegroundEventListener(self, listener):
        self.foregroundEventListener.add(listener)

    def unregisterForegroundEventListener(self, listener):
        self.foregroundEventListener.remove(listener)

    def InitDemo(self, demoinfo):
        wp = WindowProperties()
        wp.setForeground(True)
        base.win.requestProperties(wp)
        self.loadnext = demoinfo
        self.pending = True
        taskMgr.doMethodLater(0.5, self.InitDemoLater, "initdemo")


    def InitDemoLater(self, task):
        demoinfo = self.loadnext
        if demoinfo == None:
            demo=None
        else:
            path,mod,demo,title,info = demoinfo
        if self.currentdemo == demoinfo:
            return
        base.bufferViewer.enable(False)
        ModelPool.releaseAllModels()
        #ModelPool.garbageCollect()
        ShaderPool.releaseAllShaders()
        ShaderPool.garbageCollect()
        #ShaderPool.listContents(sys.stdout)
        TexturePool.releaseAllTextures()
        #TexturePool.garbageCollect()
       	#MaterialPool.releaseAllMaterials()

        if self.currentdemo != None:
            self.ClearKeys()
            self.currentdemo[2].ClearScene()
            diff = len(sys.path) - self.pathlen
            if diff > 0:
                sys.path = sys.path[:-diff]
        base.setBackgroundColor(0.5, 0.5, 0.5)
        base.camLens.setFov(self.saveFov)

        self.currentdemo = demoinfo
        if demo != None:
            # set the loader paths
            # save the search path length, restore to original len
            # when switch back
            self.pathlen = len(sys.path)
            preparePaths(
                Filename(self.cwd + os.sep + path).toOsGeneric(),
                Filename(self.cwd + os.sep + 'share').toOsGeneric())
            #render.setShaderOff() # turn off the auto shader by default
            render.clearShader()
            render.setRenderModeFilled()
            render.setAntialias(AntialiasAttrib.MAuto)
            render2d.setAntialias(AntialiasAttrib.MLine)
            demo.InitScene()
            self.SetFocus()

        if self.wxApp != None:
            self.wxApp.LoadAttrsPanel()


        if self.pendingcompile:
            self.pendingcompile = False
            self.recompile()

        return Task.done

    def SetFocus(self):
        if self.wxApp != None:
           self.wxApp.setFocus()

    def ClearKeys(self):
        for key in self.keys:
            self.ignore(key)
        self.keys.clear()

    def Ready(self):
        return self.ready
    #########################################################################3
    # these method will be called only when wx framework is not available
    def DeactivateGUI(self):
        if not self.fMouseDisabled:
            mat=Mat4(camera.getMat())
            mat.invertInPlace()
            base.mouseInterfaceNode.setMat(mat)
            base.enableMouse()
        self.wxApp.Deactivate()
        self.guiOn = False
        self.ready = True

    def ActivateGUI(self):
        # hack into base class, because I need to disableMouse
        self.fMouseDisabled = True
        if base.mouse2cam:
            self.fMouseDisabled = (base.mouse2cam.getParent() == base.dataUnused)
        if not self.fMouseDisabled:
            base.disableMouse()
        self.wxApp.Activate()
        self.guiOn = True
        self.ready = False

    def ToggleGUILater(self, task):
        if not self.guiOn:
            self.ActivateGUI()
        else:
            self.DeactivateGUI()
        return task.done

    def ToggleGUI(self):
        self.ready = self.guiOn
        # do it later, allow camera handler or other handle paused
        taskMgr.doMethodLater(0.1, self.ToggleGUILater, "togglegui")
    #########################################################################3

    def Destroy(self):
        self.ClientAcquire()
        self.ClearAllModules()
        self.removeAllTasks()
        self.ignoreAll()
        self.wxApp = None
        self.ClientRelease()
        taskMgr.removeTasksMatching("*")

    def Ignore(self,key):
        if key in self.keys:
            self.keys.remove(key)
            self.ignore(key)

    def Accept(self,key,func,extraArgs=[]):
        if key not in self.keys:
            self.keys.add(key)
        self.accept(key, func, extraArgs)

    def ClientAcquire(self):
        if self.fMultithread:
            self.pandalock.acquire()
            self.entrylock.acquire()
    def ClientRelease(self):
        if self.fMultithread:
            self.entrylock.release()
            self.pandalock.release()

    def ThreadDispatch(self):
        self.entrylock.release()
        self.pandalock.acquire()
        self.entrylock.acquire()
        self.pandalock.release()


    def getDemoInformation(self, democlass):
        title = ""
        info = ""
        if democlass != None and democlass.__doc__ != None:
            allinfo = democlass.__doc__.strip()
            sep = allinfo.find("\n")
            if sep >= 1:
                title = allinfo[0:sep]
                info = allinfo[sep+1:]
            else:
                title = allinfo

        if len(info) == 0:
            info = "No information available"
        if len(title) == 0:
            title = "Undefined"

        return title, info


    ######################################################################
    def MessageBox(self, title, msg):
        if self.wxApp:
            self.wxApp.MessageBox(title, msg)
        else:
            print title
            print msg

    def ShowDemoSource(self):
        path,mod,demo,title,info = self.currentdemo
        self.ShowSource(filename=mod.__file__[0:-1])

    def ShowSource(self, filename=None, text=None, nosave=False):
        if self.wxApp:
            self.wxApp.ShowSource(filename, text, nosave)

    def ShowSceneGraph(self):
        if self.wxApp:
            self.wxApp.ShowSceneGraph()

    def GetListSelector(self, title, listinfo):
        if self.wxApp:
            return self.wxApp.GetListSelector(title, listinfo)


def handleWxEvents(wxApp, task):
    while wxApp.evtLoop.Pending(): wxApp.evtLoop.Dispatch()
    wxApp.ProcessIdle()
    if task != None and wxApp.running:
        return task.cont

### this task let wxpython update
### panda will be frozen if user drag the python windows or etc.
##def handleWxEvents(wxApp, task):
##    while wxApp.Pending():
##        wxApp.Dispatch()
##        if wxApp.frame.dying:
##            return task.stop
##
##    return task.cont

# this task release the semaphore and allow other program to update panda at this time slice
# it only works for one single thread case
# not sure if more than 1 threads pending
def handleThreadEvents(room, task):
    room.ThreadDispatch()
    return task.cont

##def startOld(fMultithread, demolist):
##    wp = WindowProperties()
##    wp.setTitle("Demo Master")
##    wp.setOrigin(0,100)
##    base.win.requestProperties(wp)
##    room = Container(fMultithread, demolist)
##    if fMultithread:
##        # use multithreaded Wx
##        wxmain = wxDemoControl.WxMainApp(None, room)
##        wxmain.Start()
##        taskMgr.add(handleThreadEvents, 'handleThreadEvents', extraArgs=[room], appendTask=True)
##    else:
##        wxApp = wxDemoControl.myApp(room)
##        taskMgr.add(handleWxEvents, 'handleWxEvents', extraArgs=[wxApp], appendTask=True)
def start(fMultithread, demolist):
    import wxDemoControl
    wp = WindowProperties()
    wp.setTitle("Demo Master")
    wp.setOrigin(0,25)
    base.win.requestProperties(wp)

    if fMultithread:
        # use multithreaded Wx
        wxmain = wxDemoControl.WxMainApp(None, None)
        wxmain.Start()
        while not hasattr(wxmain, "app"):
            time.sleep(1)
        room = Container(fMultithread, demolist, wxmain.app)
        wxmain.app.setPandaWorld(room)
        #taskMgr.add(handleThreadEvents, 'handleWxEvents', extraArgs=[room], appendTask=True)
    else:
        wxApp = wxDemoControl.myApp(None)
        #wxApp = wxDemoControl.myAppDummy(None)
        room = Container(fMultithread, demolist, wxApp)
        wxApp.setPandaWorld(room)
        taskMgr.add(handleWxEvents, 'handleWxEvents', extraArgs=[wxApp], appendTask=True)

