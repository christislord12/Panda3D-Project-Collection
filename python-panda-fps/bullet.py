from pandac.PandaModules import *
from math import *
from time import time

class BulletClass:
    def __init__(self, position, heading, velocity, lifeTime = 5):
        #print "bullet", position, headingH, headingP, headingR, velocity
        headingH = heading.x
        headingP = heading.y
        headingR = heading.z
        
        self.node = loader.loadModel('resources/models/bullet')
        self.node.setPos(position)
        
        self.node.setH(headingH+90)
        self.node.setP(headingP)
        self.node.setR(headingR)
        
        self.node.reparentTo(render)
        self.velocity = velocity
        
        self.calcMovement()
        
        self.node.setScale(0.05)
        
        taskMgr.add(self.movement, "Bullet movement")
        
        self.lifeTime = lifeTime
        self.creationTime = time()
    
    def calcMovement(self):
        # azimuthal and radials
        azimuthal = radians(90 - base.camera.getP())
        polar = radians(self.node.getH())
        
        
        
        # Calculate XYZ step deltas
        self.stepVelocity = Vec3()
        self.stepVelocity.x = self.velocity * sin(azimuthal) * cos(polar)
        self.stepVelocity.y = self.velocity * sin(azimuthal) * sin(polar)
        self.stepVelocity.z = self.velocity * cos(azimuthal)
        
        #print "calc to (polar,azimuthal)", degrees(polar), degrees(azimuthal), "radians", polar, azimuthal, "movement", str(self.stepVelocity)
    
    def movement(self, taskdata):
        self.node.setPos(self.node.getPos() + self.stepVelocity)
        if self.creationTime + self.lifeTime < time():
            base.bulletManager.removeBullet(self)
            return
        #self.node.setY(self.node.getY() + self.velocity)
        return taskdata.cont