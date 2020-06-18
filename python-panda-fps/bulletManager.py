from pandac.PandaModules import *
from math import *
from time import time

from bullet import BulletClass

class bulletManager:
    bullets = []
    
    def __init__(self):
        pass
    
    def makeBullet(self, position = Vec3(0), heading = Vec3(0), velocity = 0, lifeTime = 5):
        bullet = BulletClass(position, heading, velocity, lifeTime)
        self.bullets.append(bullet)
    
    def removeBullet(self, bullet):
        ID = self.bullets.index(bullet)
        popBullet = self.bullets.pop(ID)
        assert bullet == popBullet
        
        bullet.node.removeNode()
        #bullet.delete()

base.bulletManager = bulletManager()