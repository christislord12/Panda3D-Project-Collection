from interactiveTexture import *
from GuiBase import *

class testgui(GuiBase):
    def objects(self):
        objects = []
        #objects.append(DirectEntry(text = "" ,scale=0.1, initialText="Type Something", numLines = 2,focus = 1, parent = self.it.renderRoot, pos = (-1.1, 0, 0.1)))
        self.directButtonSample()
        self.objects.append(self.textObject)
        self.objects.append(self.button)
        
        self.instruction = OnscreenText(
            text = "Move the mouse to move the cursor on the texture\n[f1] -- Rotate camera left\n[f2] -- Rotate camera right\n[f3] -- Rotate camera up\n[f4] -- Rotate camera down\n",
            pos = (-1.7, -0.25), 
            scale = 0.07,
            align=TextNode.ALeft,
            parent = self.it.renderRoot)
        
        return objects
    
    def setText(self):
        bk_text = "Button Clicked"
        self.textObject.setText(bk_text)
    
    def directButtonSample(self):
        # Add some text
        bk_text = "This is my Demo"
        self.textObject = OnscreenText(
            text = bk_text,
            pos = (0.95,-0.95), 
            scale = 0.07,
            fg=(1,0.5,0.5,1),
            align=TextNode.ACenter,
            mayChange=1,
            parent = self.it.renderRoot)
        
        # Add button
        self.button = DirectButton(text = ("OK", "click!", "rolling over", "disabled"), scale=0.1, command=self.setText, parent = self.it.renderRoot, pos = (0.5, 0, 0.5))