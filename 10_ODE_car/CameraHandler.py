from direct.directbase import DirectStart
from direct.showbase import DirectObject 
from pandac.PandaModules import Vec3
import math

class CameraHandler(DirectObject.DirectObject):
  def __init__(self):
    base.disableMouse()    
    base.camera.setPos(0,20,20)
    base.camera.lookAt(0,0,0)
    self.moveByMouse=True
    self.mx,self.my=0,0
    self.dragging=False
    self.target=Vec3()
    self.camDist=40   
    self.setTarget(0,0,0)
    self.accept("mouse3",self.startDrag)
    self.accept("mouse3-up",self.stopDrag)
    self.accept("wheel_up",lambda : self.adjustCamDist(0.9))
    self.accept("wheel_down",lambda : self.adjustCamDist(1.1))
    taskMgr.add(self.dragTask,'dragTask')    
  def turnCameraAroundPoint(self,tx,ty,p,dist):
        newCamHpr=Vec3()         
        camHpr=base.camera.getHpr()
        newCamHpr.setX(camHpr.getX()+tx)
        newCamHpr.setY(camHpr.getY()-ty)
        newCamHpr.setZ(camHpr.getZ())
        base.camera.setHpr(newCamHpr)
        angleradiansX = newCamHpr.getX() * (math.pi / 180.0)
        angleradiansY = newCamHpr.getY() * (math.pi / 180.0)
        base.camera.setPos( dist*math.sin(angleradiansX)*math.cos(angleradiansY)+p.getX(),
                           -dist*math.cos(angleradiansX)*math.cos(angleradiansY)+p.getY(),
                           -dist*math.sin(angleradiansY)+p.getZ() )
        base.camera.lookAt(p.getX(),p.getY(),p.getZ())                
  def setTarget(self,x,y,z):
    self.target.setX(x)
    self.target.setY(y)
    self.target.setZ(z)
    self.turnCameraAroundPoint(0,0,self.target,self.camDist)
  def startDrag(self):
    self.dragging=True
  def stopDrag(self):
    self.dragging=False
  def adjustCamDist(self,aspect):
    self.camDist=self.camDist*aspect
    self.turnCameraAroundPoint(0,0,self.target,self.camDist)
  def dragTask(self,task):
    if base.mouseWatcherNode.hasMouse():
        mpos = base.mouseWatcherNode.getMouse()  
        if self.dragging:
            self.turnCameraAroundPoint((self.mx-mpos.getX())*100,(self.my-mpos.getY())*100,self.target,self.camDist)        
        else:
            moveY=False
            moveX=False
            if self.my>0.8:
                angleradiansX = base.camera.getH() * (math.pi / 180.0)
                aspect=(1-self.my-0.2)*5
                moveY=True
            if self.my<-0.8:
                angleradiansX = base.camera.getH() * (math.pi / 180.0)+math.pi
                aspect=(1+self.my-0.2)*5
                moveY=True
            if self.mx>0.8:
                angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5
                aspect2=(1-self.mx-0.2)*5
                moveX=True
            if self.mx<-0.8:
                angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5
                aspect2=(1+self.mx-0.2)*5
                moveX=True                                
            if not self.moveByMouse:
                moveX=False
                moveY=False    
            if moveY:    
                self.target.setX(self.target.getX()+math.sin(angleradiansX)*aspect)
                self.target.setY(self.target.getY()-math.cos(angleradiansX)*aspect)
                self.turnCameraAroundPoint(0,0,self.target,self.camDist)
            if moveX:    
                self.target.setX(self.target.getX()-math.sin(angleradiansX2)*aspect2)
                self.target.setY(self.target.getY()+math.cos(angleradiansX2)*aspect2)
                self.turnCameraAroundPoint(0,0,self.target,self.camDist)                
        self.mx=mpos.getX()
        self.my=mpos.getY()                               
    return task.cont   