from interactiveTexture import *

class GuiBase:
    def __init__(self, world, name="gui", xSize=2048, ySize=2048):
        self.it = interactiveTexture("demo", xSize, ySize)
        self.itTex = self.it.getTexture()
        self.world = world
        
    def objects(self):
        """ To be added by gui class """
        objects = []
        return objects
    
    def do(self):
        #for object in self.objects():
            #object.setTexture(self.itTex, 1)
        #self.it.enable()
        self.modelNode = self.world.find("-PandaNode")
        
        self.screens = []
        for childNode in self.modelNode.getChildren():
            if childNode.getTag("type") == "screen":
                childNode.setTexture(self.itTex, 1)
                self.screens.append(childNode)
        
        self.it.enable()