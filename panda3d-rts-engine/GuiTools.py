#!/usr/bin/env python
import __builtin__ 
from direct.showbase import DirectObject
from direct.actor import Actor
from direct.task import Task 
import libpanda 
from pandac.PandaModules import Vec4, CardMaker, LineSegs, Point2, Point3 

import math 




class mouseSelectTool(DirectObject.DirectObject):
    

    def __init__(self,pickableList = []):
        self.pickable = pickableList
        tempCard = CardMaker('')
        tempCard.setFrame(0,1,0,1)

        #Lets render our frame so we can hide / show /resize it as needed        
        self.selectFrame = render2d.attachNewNode(tempCard.generate())
        self.selectFrame.setColor(1,1,0,.2)
        self.selectFrame.setTransparency(1)
        self.selectFrame.hide()
        
        #Set up our line segmants for a border 
        ls = LineSegs()
        ls.moveTo(0,0,0)
        ls.drawTo(1,0,0)
        ls.drawTo(1,0,1)
        ls.drawTo(0,0,1)
        ls.drawTo(0,0,0)
        
        self.selectFrame.attachNewNode(ls.create())
        
        self.selected = []
        self.previousSelect = []
        self.selectable = []
        
        #Init our mouse locations
        self.pt2InitMousePos = (-1,-1)
        self.pt2LastMousePos = (-1,-1)
        self.fFovh , self.fFovv = base.camLens.getFov()
        
        self.fTimeLastUpdateRect = 0
        self.fTimeLastUpdateSelected = 0
        self.UpdateTimeRect = 0.015
        self.UpdateTimeSelected = 0.015
        
        print "Running Select Tools"
        
        self.accept("mouse1",self.OnStartSelect)
        self.accept("control-mouse1",self.OnStartSelect)
        self.accept("mouse1-up",self.OnMouseRelease)
        self.taskUpdateSelectRect = 0
        
        
       
    def isMouseInWindow(self):
        return base.mouseWatcherNode.hasMouse
       
    def OnStartSelect(self):
        if(not self.isMouseInWindow()):
            return
        
        #Lets clear our last selection
        for selected in self.previousSelect:
            print "Hiding bounds for ",selected
            selected.hideBounds()
            
        
        self.selecting = True
        self.pt2InitMousePos = Point2(base.mouseWatcherNode.getMouse())
        self.pt2LastMousePos = Point2(self.pt2InitMousePos)
        
        self.selectFrame.setPos(self.pt2InitMousePos[0],1,self.pt2InitMousePos[1])
        self.selectFrame.setScale(1e-3,1,1e-3)
        self.selectFrame.show()
        
        self.taskUpdateSelectRect = taskMgr.add(self.UpdateSelectRect,"UpdateSelectRect")
        self.taskUpdateSelectRect.lastMpos = None
        
        return
        
        
        
    def OnMouseRelease(self):
        if not(self.isMouseInWindow()):
            return task.cont
        if(self.taskUpdateSelectRect != 0):
            taskMgr.remove(self.taskUpdateSelectRect)
                        

        #Lets see if our mouse moved at all
        if (abs(self.pt2InitMousePos[0] - self.pt2LastMousePos[0])  <= .01) & (abs(self.pt2InitMousePos[1] - self.pt2LastMousePos[1])  <= .01):
            # we didn't move, so this is a single selection
        
            for i in self.selectable:
                
                #Get our distance from the camera (though i don't get the math)
                fTempObjDist = 2*(base.camLens.getFar())**2 
               
                #Get the bounds of the object
                sphBounds = i.getBounds()
                
                #Lets get our point in 3d space of the object in question
                p3 = base.cam.getRelativePoint(i.getParent(), sphBounds.getCenter())
                
                #Lets get the radius of said object
                r = sphBounds.getRadius()
                
                #Ok so we are obviously getting the screen width here .All be it complicated - and over my head :-)
                #radius / (X * tangent(radians(FieldOfView Horizontal / 2))) 
                screen_width = r/(p3[1]*math.tan(math.radians(self.fFovh/2)))
                
                #radius  / (X * tangent(radians(FieldOfView Vertical /2))) 
                screen_height = r/(p3[1]*math.tan(math.radians(self.fFovv/2)))
                
                #Lets get our point in a 2d Field
                p2 = Point2() 
                base.camLens.project(p3, p2)
                
                
                #Ok lets make sure our mouse position is roughly inside the bounds of the object in question                
                if (self.pt2InitMousePos[0] >= (p2[0] - screen_width/2)): 
                   if (self.pt2InitMousePos[0] <= (p2[0] + screen_width/2)): 
                      if (self.pt2InitMousePos[1] >= (p2[1] - screen_height/2)): 
                         if (self.pt2InitMousePos[1] <= (p2[1] + screen_height/2)):
                            
                            #We check the obj's distance to the camera and choose the closest one
                            #Umm what? Me = no understand
                            dist = p3[0]**2+p3[1]**2+p3[2]**2 - r**2 
                            if dist < fTempObjDist: 
                               fTempObjDist = dist 
                               self.previousSelect.append(i)
                               i.showBounds()
            
            
        self.selectFrame.hide()
        self.selecting = False
        
        
        return
        
    
    def UpdateSelectRect(self,task):
        
        if not(self.isMouseInWindow()):
            return task.cont
        
        mpos = base.mouseWatcherNode.getMouse()
        t = globalClock.getRealTime()
        if(self.pt2LastMousePos != mpos  ):
            self.MouseMoved = True
            if(t - self.fTimeLastUpdateRect) > self.UpdateTimeRect:
                #Set our lastUpdateRect time to now
                self.fTimeLastUpdateRect = t
                
                #Lets set our last point to our current point
                self.pt2LastMousePos = Point2(mpos)
                
                #Lets update our Select Rectangle
                d = self.pt2LastMousePos - self.pt2InitMousePos
                
                #self.selectFrame.setScale(d[0] if d[0] else 1e-3, 1, d[1] if d[1] else 1e-3)
                #Easier to understand
                mx = d[0]
                my = d[1]
                if not (mx):
                    #mx = 1*10 ^ -3 (Thx Andrew Mann )
                    mx = 1e-3
                if not(my):
                    my = 1e-3

                #Set our scale                    
                self.selectFrame.setScale(mx,1,my)
                
            #Lets look to see if our mouse has moved
            if (abs(self.pt2InitMousePos[0] - self.pt2LastMousePos[0]) > .01) & (abs(self.pt2InitMousePos[1] - self.pt2LastMousePos[1]) > .01):
                if (t - self.fTimeLastUpdateSelected) > self.UpdateTimeSelected:
                    self.fTimeLastUpdateSelected = t
                    self.previousSelect = self.selected
                    self.selected = []
                    
                    #Lets get the four corners of our rect
                    frameMouseLeftX = min(self.pt2InitMousePos[0],self.pt2LastMousePos[0])
                    frameMouseLeftY = max(self.pt2InitMousePos[1],self.pt2LastMousePos[1])
                    frameMouseRightX = max(self.pt2InitMousePos[0],self.pt2LastMousePos[0])
                    frameMouseRightY = min(self.pt2InitMousePos[1],self.pt2LastMousePos[1])
                   
                    #Itterate through our selectable items and find check each one's bounds. See if they are in our rectangle.. 
                    for i in self.selectable:
                        sphBounds = i.getBounds()
                        print "Bounds : ",i.getBounds()
                        print "Get Parent :",i.getParent()
                        print "Get Center :",sphBounds.getCenter()
                        p3 = base.cam.getRelativePoint(i.getParent(), sphBounds.getCenter())
                        p2 = Point2() 
        
                        #Lets make sure that the point I am specifing can be converted to a 2d point
                        if base.camLens.project(p3, p2):
                            
                            #Lets  Make sure that the point falls within our rectangle
                            if (p2[0] >= frameMouseLeftX) & (p2[0] <= frameMouseLeftY) & (p2[1] >= frameMouseRightY) & (p2[1] <= frameMouseLeftY):
                                self.selected.append(i)
                                i.showBounds()
        return Task.cont
                
                
        
            
 
        

    
        
        

