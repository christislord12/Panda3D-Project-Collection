from panda3d.core import *
import random, math


class Asteroid:
    
    def __init__(self, pos, hpr, size):
        scales = {1:(1,3), 2:(4,6), 3:(8,15)}
        self.pos = pos
        self.hpr = hpr
        self.size = size
        self.scale = random.randrange(*scales[self.size])
        self.speed = None
        self.rspeed = None

class Generator:
    
    def __init__(self):
        self.template = {1:((15,25),(15,50)),
                        2:((2,5),(25, 40)),
                        3:((1,3),(5,30))}
        self.models = {1:'asteroid_s', 2:'asteroid', 3:'asteroid'}
        self.a_list = []
        self.root = render.attachNewNode('a_root')
        self._rec_gen(3, Vec3(0, 0, 0))
        self.load()

    def _rec_gen(self, size, base_pos):
        if size > 0:
            for i in range(random.randrange(*self.template[size][0])):
                azmt = random.random() * 2 * math.pi
                incl = random.random() * math.pi
                r = random.randrange(*self.template[size][1]) + random.random()
                x = r * math.sin(incl) * math.cos(azmt)
                y = r * math.sin(incl) * math.sin(azmt)
                z = r * math.cos(incl)
                pos = Vec3(x, y, z) + base_pos
                hpr = Vec3(random.random() * 360, 
                           random.random() * 360, 
                           random.random() * 360)
                new_ast = Asteroid(pos, hpr, size)
                self.a_list.append(new_ast)
                self._rec_gen(size - 1, pos)
                
    def load(self):
        for a in self.a_list:
            mdl = loader.loadModel(self.models[a.size])
            mdl.setPosHpr(a.pos, a.hpr)
            mdl.setScale(a.scale)
            mdl.reparentTo(self.root)
                


class Sun():
    def __init__(self, pos, color):
        self.root = render.attachNewNode('sun_root')
        cm = CardMaker('card')
        card = self.root.attachNewNode(cm.generate())
        card.setBillboardPointEye()
        card.setTexture(loader.loadTexture('tex/flare5.png'))
        #card.setColor(color)
        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setPos(pos)
        card.setScale(20)
        card.setLightOff()
        self.light = self.set_light(card, color)
        taskMgr.add(self.update, 'sun_update')
        
    def set_light(self, root, color):
        #dlight = DirectionalLight('dlight')
        #dlight.setColor(Vec4(1, 0.8, 0.6, 1))
        #dlnp = root.attachNewNode(dlight)
        #render.setLight(dlnp)
        #return dlnp
        plight = PointLight('plight')
        plight.setColor(color)
        plnp = root.attachNewNode(plight)
        render.setLight(plnp)
        return plnp
        
    def update(self, task):
        self.root.setHpr(self.root.getHpr() + Vec3(0.05, 0.05, 0.05))
        #self.light.lookAt(0,0,0)
        return task.cont

def make_scene():
    Sun(Vec3(0, 50, 0), Vec4(1, 0.95, 0.8, 1))
    Sun(Vec3(50, -50, 50), Vec4(0.8, 0.95, 1.0, 1))
    g = Generator()
    g.root.setShaderAuto()

