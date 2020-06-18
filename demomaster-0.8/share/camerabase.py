from demobase import *
from direct.interval.IntervalGlobal import LerpFunc
from pandac.PandaModules import TextNode


#class Att_Camera(Att_base):
#    def __init__(self, container, fReadOnly, name,  minpos, maxpos, pitchrange, headingrange, focus, rate=0.2, posrange=[-250,250],NodeName=None):
#        Att_base.__init__(self, fReadOnly, name, NodeName=NodeName)

class Att_CameraControllerByMouse(Att_base):
    LOCK_POS = 1
    LOCK_AT = 1
    def __init__(self, container, fReadOnly, name,  minpos, maxpos, pitch, heading, focus, rate=0.2, posrange=[-250,250],fov=[5.0,100.0,0.0], speed=30, distance=5,NodeName=None):
        Att_base.__init__(self, fReadOnly, name, NodeName=NodeName)
        posrange0 = min(posrange[0], min(minpos))
        posrange1 = max(posrange[1], max(maxpos))
        self.container = container
        self.container.registerForegroundEventListener(self)
        self.att_rate= Att_FloatRange(fReadOnly, "Rate", 0.01, 5, rate)
        self.att_movingspeed = Att_FloatRange(fReadOnly, "Speed", 0, 500, speed)
        self.att_minpos = Att_Vecs(fReadOnly, "Minpos", 3, minpos, posrange0, posrange1)
        self.att_maxpos = Att_Vecs(fReadOnly, "Maxpos", 3, maxpos, posrange0, posrange1)
        self.att_pitch = Att_FloatRange(fReadOnly, "Pitch", pitch[0], pitch[1], pitch[2], 1)
        self.att_heading = Att_FloatRange(fReadOnly, "Heading", heading[0], heading[1], heading[2], 1)
        self.att_focus = Att_Vecs(fReadOnly, "Focus", 3, focus, posrange0, posrange1)

        v = fov[2]
        if v == 0.0:
            df = base.camLens.getFov()
            v = df[0]
        self.att_fov = Att_FloatRange(fReadOnly, "Fov", fov[0], fov[1], v, 1)
        self.att_fov.setNotifier(self.setFov)
        self.originalfov = v

        # Set the current viewing target
        self.mousex = 0
        self.mousey = 0
        self.last = 0
        self.mousebtn = [0,0,0]

        base.disableMouse()
        #base.camera.setPos(pos[0], pos[1], pos[2])
        #base.camera.lookAt(lookat[0], lookat[1], lookat[2])

        self.container = container
        self.stopped=True
        self.fForeground = self.container.fForeground
        self.lock = 0
        #self.clickToResume = False
        self.zoomed = False

        base.camera.setHpr(self.att_heading.v,self.att_pitch.v,0)
        self.distance = distance
        #dir = base.camera.getMat().getRow3(1)
        #focus = self.att_focus.getValue()
        #base.camera.setPos(focus - (dir*self.distance))

        self.zooming=False
        self.setFov(None)
        self.screenText=None
        self.SetupController()
        self.SetFocus(focus)
        self.Resume()

    def ShowPosition(self, textnode, x=0.65, y=0.85):
        if self.screenText != None:
            self.screenText.destroy()
        self.screenText = addInstructions(x,y,"", align=TextNode.ALeft, node=textnode)
        #print self.screenText

    def SetupController(self):
        self.functionDict = {
            "zoomin":self.ZoomIn,
            "zoomout":self.ZoomOut,
            "stop":self.Stop,
            "resume":self.Resume,
            "forward":self._KeySet,
            "backward":self._KeySet,
            "moveup":self._KeySet,
            "movedown":self._KeySet,
            "moveleft":self._KeySet,
            "moveright":self._KeySet,
            "fovup":self._setFovUp,
            "fovdown":self._setFovDown,
        }
        self.keystate = {
            "forward":0,
            "backward":0,
            "moveup":0,
            "movedown":0,
            "moveleft":0,
            "moveright":0,
        }
        self.keymap = {}

    def GetDefaultInstruction(self):
        return """Press ESC to release mouse, Enter to resume mouse control
Move mouse to rotate camera
Use wheel to set Fov
Left mouse button to move forwards
Right mouse button to move backwards
w,s,a,d key to move up down left right
f,g key to quick zoom in and out"""

    # application should call this function or they can call the other api direction
    def DefaultController(self, forward=["mouse1"], backward=["mouse2", "mouse3"], zoomin=["f"],
            zoomout=["g"], stop=["escape"], resume=["enter"],
            moveup=["w"], movedown=["s"], moveright=["d"], moveleft=["a"],
            fovup=["wheel_down"], fovdown=["wheel_up"]
            ):

        for key in self.keymap:
            self.container.Ignore(key)
            if len(key) == 1 or key.find("mouse")== 0:
                self.container.Ignore(key+"-up")
        self.keymap = {}
        if forward:
            for n in forward:
                self.keymap[n] = "forward"
        if backward:
            for n in backward:
                self.keymap[n] = "backward"
        if zoomin:
            for n in zoomin:
                self.keymap[n] = "zoomin"
        if zoomout:
            for n in zoomout:
                self.keymap[n] = "zoomout"
        if stop:
            for n in stop:
                self.keymap[n] = "stop"
        if moveup:
            for n in moveup:
                self.keymap[n] = "moveup"
        if movedown:
            for n in movedown:
                self.keymap[n] = "movedown"
        if moveright:
            for n in moveright:
                self.keymap[n] = "moveright"
        if moveleft:
            for n in moveleft:
                self.keymap[n] = "moveleft"
        if fovup:
            for n in fovup:
                self.keymap[n] = "fovup"
        if fovdown:
            for n in fovdown:
                self.keymap[n] = "fovdown"

        # resume key handling is special
        if resume:
            for n in resume:
                self.container.Accept(n, self.Resume)

        self.setMouseCondition()

    def _KeySet(self, key, value):
        #print "Key set", key, value
        self.keystate[key] = value

    def _setFovDelta(self, value):
        if self.zooming:
            return
        self.setFov(None, self.att_fov.v + value)

    def _setFovUp(self, funcname=None, value=None):
        self._setFovDelta((self.att_fov.maxv - self.att_fov.minv) / 30);

    def _setFovDown(self, funcname=None, value=None):
        self._setFovDelta(- (self.att_fov.maxv - self.att_fov.minv) / 30);

    def setFov(self, object, v=None):
        if v != None:
            self.att_fov.v = v
            self.att_fov.fix()

        base.camLens.setFov(self.att_fov.v)
        if v == None:
            self.notify()

    def fovSet(self, t, restore):
        self.setFov(None, t)
        if restore:
            if t == self.originalfov:
                self.zooming = False

    def ZoomIn(self, funcname=None, value=None):
        #print "zoomin"
        if value != None and value == 0:
            self.ZoomRestore()

        if self.zooming:
            return
        self.originalfov = self.att_fov.v
        fovZoomer = LerpFunc(self.fovSet, 0.1, self.att_fov.v, self.att_fov.minv, 'easeOut', [False], "zoomer")
        fovZoomer.start()
        self.zooming = True

    def ZoomRestore(self):
        #print "zoomrestore"
        if not self.zooming:
            return
        fovZoomer = LerpFunc(self.fovSet, 0.1, self.att_fov.v, self.originalfov, 'easeIn', [True], "zoomer")
        fovZoomer.start()
        #self.zooming = False

    def ZoomOut(self, funcname=None, value=None):
        if value != None and value == 0:
            self.ZoomRestore()
        #print "Zoom out"
        if self.zooming:
            return
        self.originalfov = self.att_fov.v
        fovZoomer = LerpFunc(self.fovSet, 0.1, self.att_fov.v, self.att_fov.maxv, 'easeOut', [False], "zoomer")
        fovZoomer.start()
        self.zooming = True


    #def SetClickToResume(self, v=True):
    #    self.clickToResume = v

    def forgroundEventHandler(self, fForeground):
        self.fForeground = fForeground
#        if self.fForeground and not self.stopped:
#            base.win.movePointer(0, 400, 300)
        if not self.stopped:
            self.setMouseCondition()

    def Destroy(self):
        self.container.unregisterForegroundEventListener(self)
        self.Stop()
        if self.screenText != None:
            self.screenText.destroy()
            self.screenText=None

    def Stop(self, funcname=None, value=None):
        if value != None and value == 0:
            return
        if self.stopped:
            return
        self.stopped = True
        self.setMouseCondition()


    def Resume(self, funcname=None, value=None):
        if value != None and value == 0:
            return
        if not self.stopped:
            return
        self.stopped = False
        #print "Resumed"
        dir = base.camera.getMat().getRow3(1)
        focus = base.camera.getPos() + (dir*self.distance)
        self.att_focus.setValue(focus)

        if self.fForeground:
            base.win.movePointer(0, 400, 300)

        self.setMouseCondition()


    def setMouseCondition(self):
        #print "stopped", self.stopped, "foreground", self.fForeground
        if not self.stopped and self.fForeground:
##            self.container.Accept("mouse1", self.setMouseBtn, [0, 1])
##            self.container.Accept("mouse1-up", self.setMouseBtn, [0, 0])
##            self.container.Accept("mouse2", self.setMouseBtn, [1, 1])
##            self.container.Accept("mouse2-up", self.setMouseBtn, [1, 0])
##            self.container.Accept("mouse3", self.setMouseBtn, [2, 1])
##            self.container.Accept("mouse3-up", self.setMouseBtn, [2, 0])
            for key in self.keymap:
                functionname = self.keymap[key]
                function = self.functionDict[functionname]
                #print key,functionname,function
                self.container.Accept(key, function, [functionname, 1])
                if len(key) == 1 or key.find("mouse")== 0:
                    self.container.Accept(key + "-up", function, [functionname, 0])

            base.disableMouse()
            taskMgr.add(self.controlCamera, "CameraControllerByMouse")
            props = WindowProperties()
            props.setCursorHidden(True)
            base.win.requestProperties(props)
            base.win.movePointer(0, 400, 300)
        else:
            for key in self.keymap:
                self.container.Ignore(key)
                if len(key) == 1 or key.find("mouse")== 0:
                    self.container.Ignore(key+"-up")

            props = WindowProperties()
            props.setCursorHidden(False)
            base.win.requestProperties(props)

            mat=Mat4(camera.getMat())
            mat.invertInPlace()
            base.mouseInterfaceNode.setMat(mat)
            base.enableMouse()
            taskMgr.remove("CameraControllerByMouse")

##    def setMouseBtn(self, btn, value):
##        if self.stopped and self.clickToResume:
##            base.win.movePointer(0, 100, 100)
##            self.Resume()
##
##        self.mousebtn[btn] = value

    def LockAt(self, focus=None, distance=None):
        if focus != None:
            self.att_focus.setValue(focus)
        if distance != None:
            self.distance = distance
        else:
            pos = base.camera.getPos()
            focus = self.att_focus.getValue()
            self.distance = (pos-focus).length()


        focus = self.att_focus.getValue()
        dir = base.camera.getMat().getRow3(1)
        dir.normalize()
        pos = focus - (dir*self.distance)
        base.camera.setPos(pos)

        self.lock = self.LOCK_AT
        self.setMouseCondition()

    def LockPosition(self, pos=None):
        if pos != None:
            base.camera.setPos(pos)
        dir = base.camera.getMat().getRow3(1)
        dir.normalize()
        focus = base.camera.getPos() + (dir*self.distance)
        self.att_focus.setValue(focus)
        self.lock = self.LOCK_POS
        self.setMouseCondition()

    def SetDistance(self,distance):
        self.SetFocus(distance=distance)

    def SetFocus(self, pos=None, dir=None, distance=None):
        if pos == None:
            pos = self.att_focus.getValue()
        else:
            self.att_focus.setValue(pos)
        if dir == None:
            dir = base.camera.getMat().getRow3(1)
            dir.normalize()
        if distance != None:
            self.distance = distance
        cpos = pos - (dir*self.distance)
        base.camera.setPos(cpos)
        #print pos,cpos
        if self.stopped:
            mat=Mat4(camera.getMat())
            mat.invertInPlace()
            base.mouseInterfaceNode.setMat(mat)
        self.updateScreenText()

    def UnlockPosition(self):
        self.lock = 0
        self.setMouseCondition()

    def controlCamera(self, task):
        ready = self.fForeground and self.container.Ready()

        if self.fForeground and not self.stopped and not ready:
           self.Stop()

        if ready:
            # figure out how much the mouse has moved (in pixels)
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            if base.win.movePointer(0, 400, 300):
                self.att_heading.v -= (x - 400)*self.att_rate.v
                self.att_heading.fix()
                self.att_pitch.v -= (y - 300)*self.att_rate.v
                self.att_pitch.fix()

        base.camera.setHpr(self.att_heading.v,self.att_pitch.v,0)
        elapsed = task.time - self.last
        if (self.last == 0): elapsed = 0
        speed = elapsed * self.att_movingspeed.v
        dir = base.camera.getMat().getRow3(1)
        dir.normalize()
        if (self.lock == 0 or self.lock == self.LOCK_AT) and not self.stopped:
            focus = self.att_focus.getValue()
            if ready:
                if self.lock == self.LOCK_AT:
                    if self.keystate["forward"]:
                        self.distance -= 0.1 * speed
                        self.distance = max(self.distance, 0.5)
                    if self.keystate["backward"]:
                        self.distance += 0.1 * speed
                else:
                    if self.keystate["forward"]:
                        focus = focus + dir * speed
                    if self.keystate["backward"]:
                        focus = focus - dir * speed
            pos = focus - (dir*self.distance)
            if ready:
                if self.keystate["moveup"]:
                    pos += Vec3(0,0,speed)
                if self.keystate["movedown"]:
                    pos -= Vec3(0,0,speed)
                if self.keystate["moveright"]:
                    camright = base.camera.getNetTransform().getMat().getRow3(0)
                    camright.normalize()
                    pos += camright*speed
                if self.keystate["moveleft"]:
                    camright = base.camera.getNetTransform().getMat().getRow3(0)
                    camright.normalize()
                    pos -= camright*speed
                #if self.keystate["moveup"]:
                #if self.keystate["movedown"]:
            base.camera.setPos(pos)

        if (base.camera.getX() < self.att_minpos.vec[0].v): base.camera.setX(self.att_minpos.vec[0].v)
        if (base.camera.getX() >  self.att_maxpos.vec[0].v): base.camera.setX(self.att_maxpos.vec[0].v)
        if (base.camera.getY() < self.att_minpos.vec[1].v): base.camera.setY(self.att_minpos.vec[1].v)
        if (base.camera.getY() >  self.att_maxpos.vec[1].v): base.camera.setY(self.att_maxpos.vec[1].v)
        if (base.camera.getZ() <  self.att_minpos.vec[2].v): base.camera.setZ( self.att_minpos.vec[2].v)
        if (base.camera.getZ() >  self.att_maxpos.vec[2].v): base.camera.setZ( self.att_maxpos.vec[2].v)
        if self.lock == 0:
            focus = base.camera.getPos() + (dir*self.distance)
            self.att_focus.setValue(focus)

        self.last = task.time
        self.updateScreenText()

        if ready:
            self.container.SetFocus()
            self.notify()

        return task.cont


    def updateScreenText(self):
        if self.screenText != None:
            pos = base.camera.getPos()
            hpr = base.camera.getHpr()
            focus = self.att_focus.getValue()
            self.screenText.setText("(%0.1f,%0.1f,%0.1f)\n(%0.1f,%0.1f,%0.1f)\n(%0.1f,%0.1f,%0.1f)" %
                    (pos[0],pos[1],pos[2],
                     focus[0],focus[1],focus[2],
                     hpr[0],hpr[1],hpr[2]
                    ))
