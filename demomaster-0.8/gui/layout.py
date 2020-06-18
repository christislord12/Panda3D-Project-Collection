from gui.controls import *

class Layout(Widget):
    
    def __init__(self,importfile,parent):
        Widget.__init__(self)
        self.node.hide()
        self.parent = parent
        if type(importfile) == str:
            self.src = __import__(importfile)
        else:
            self.src = importfile
            
        self.idToFrame = {}
        self.processed = set()
        self.setup(self.src.__dict__.values())
        
    def find(self,name):
        return self.idToFrame[name]
        
    def hassClasses(self,layoutDef):
        for cls in layoutDef.__dict__.values():
            if type(cls).__name__ == "classobj" and cls.__name__[1] != "_":
                return True
        return False
    
    def setup(self,objects):
        for cls in objects:
            if type(cls).__name__ == "classobj" and cls.__name__[1] != "_":
                name = cls.__name__ 
                frame = Frame()
                frame.name = name
                frame.skinType = "SELECT_BG"
                self.idToFrame[name] = frame
                self.parent.add(frame)
                self.process(name) 
                if "hide" in cls.__dict__ and cls.hide:
                    frame.hide()
                if "style" in cls.__dict__:
                    frame.skinType = cls.style
                if self.hassClasses(cls):
                    frame.addLayout(cls)
                    

    def resize(self):
        self.processed = set()
        for cls in self.src.__dict__.values():
            if type(cls).__name__ == "classobj" and cls.__name__[1] != "_":
                self.process(cls.__name__)
                
                    
    def process(self,name):
        self.processed.add(name)
        
        cls = self.src.__dict__[name]
        frame = self.idToFrame[name]
        # position pass one
        if type(cls.pos[0]) in [float,int,long]:
            x = int(cls.pos[0])
        elif cls.pos[0][-1] == "%":
            x = int(int(cls.pos[0][0:-1])/100.*self.parent.size[0])
        elif cls.pos[0] == "left":
            x = 0
        else:
            x = 0
               
        if type(cls.pos[1]) in [float,int,long]:
            y = int(cls.pos[1])
        elif cls.pos[1][-1] == "%":
            y = int(int(cls.pos[1][0:-1])/100.*self.parent.size[1])
        elif cls.pos[1] == "top":
            y = 0
        else:
            y = 0

        # size pass one
        if type(cls.size[0]) in [float,int,long]:
            sx = int(cls.size[0])
        elif cls.size[0][-1] == "%":
            sx = int(int(cls.size[0][0:-1])/100.*self.parent.size[0])
        else:
            sx = 100
        
        if type(cls.size[1]) in [float,int,long]:
            sy = int(cls.size[1])
        elif cls.size[1][-1] == "%":
            sy = int(int(cls.size[1][0:-1])/100.*self.parent.size[1])
        else:
            sy = 100
        
        # position pass 2
        if cls.pos[0] == "center":
            x = self.parent.size[0]/2-sx/2
        elif cls.pos[0] == "right":
            x = self.parent.size[0] - sx
        elif type(cls.pos[0]) == str:
            words = cls.pos[0].split()
            if len(words) > 1 and words[-1] in self.idToFrame:
                if words[-1] not in self.processed: self.process(words[-1])
                otherFrame = self.idToFrame[words[-1]]
                if words[0] == "left":
                    x = otherFrame.getPos()[0] - sx
                elif words[0] == "right":
                    x = otherFrame.getPos()[0] + otherFrame.getSize()[0]
                elif words[0] == "next":
                    x = otherFrame.getPos()[0]
            
        if cls.pos[1] == "center":
            y = self.parent.size[1]/2-sy/2
        elif cls.pos[1] == "bottom":
            y = self.parent.size[1] - sy
        elif type(cls.pos[1]) == str:
            words = cls.pos[1].split()
            if len(words) > 1 and words[-1] in self.idToFrame:
                if words[-1] not in self.processed: self.process(words[-1])
                otherFrame = self.idToFrame[words[-1]]
                if words[0] == "above":
                    y = otherFrame.getPos()[1] - sy
                elif words[0] == "bellow":
                    y = otherFrame.getPos()[1] + otherFrame.getSize()[1]
                elif words[0] == "next":
                    y = otherFrame.getPos()[1]
            
        
        # size pass 2
        if type(cls.size[0]) == str:
            words = cls.size[0].split()
            if words[0] == "grow" and words[-1] in self.idToFrame:
                if words[-1] not in self.processed: self.process(words[-1])
                otherFrame = self.idToFrame[words[-1]]
                if x < otherFrame.getPos()[0]:
                    sx = otherFrame.getPos()[0] - x
                elif x < otherFrame.getPos()[0] + otherFrame.getSize()[0]:
                    sx = otherFrame.getPos()[0] + otherFrame.getSize()[0] - x
                elif x > otherFrame.getPos()[0] + otherFrame.getSize()[0]:
                    sx = x - (otherFrame.getPos()[0] + otherFrame.getSize()[0]) + sx
                    x = otherFrame.getPos()[0] + otherFrame.getSize()[0]
                    
        if type(cls.size[1]) == str:
            words = cls.size[1].split()
            if words[0] == "grow" and words[-1] in self.idToFrame:
                if words[-1] not in self.processed: self.process(words[-1])
                otherFrame = self.idToFrame[words[-1]]
                if y < otherFrame.getPos()[1]:
                    sy = otherFrame.getPos()[1] - y
                elif y < otherFrame.getPos()[1] + otherFrame.getSize()[0]:
                    sy = otherFrame.getPos()[1] + otherFrame.getSize()[0] - y
                elif y > otherFrame.getPos()[1] + otherFrame.getSize()[0]:
                    sy = y - (otherFrame.getPos()[1] + otherFrame.getSize()[0]) + sy
                    y = otherFrame.getPos()[1] + otherFrame.getSize()[0]
            
        frame.setPos(Vec2(x,y))
        frame.setSize(Vec2(sx,sy))
        
        
        