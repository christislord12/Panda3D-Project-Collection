from pandac.PandaModules import *

class Stretch:

    def __init__(self,xStart,yStart,xEnd,yEnd):
        self.xStart,self.yStart,self.xEnd,self.yEnd = xStart,yStart,xEnd,yEnd

    def draw(self,theme,pos,size):
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]
        u,v,us,vs = self.xStart,self.yStart,self.xEnd,self.yEnd
        theme.rectStreatch((x,y,xs,ys),(u,v,us,vs))

class StretchBorder:

    def __init__(self,xStart,yStart,xEnd,yEnd,border):
        self.xStart,self.yStart,self.xEnd,self.yEnd,self.border = xStart,yStart,xEnd,yEnd,border

    def draw(self,theme,pos,size):
        u,v,us,vs,b = self.xStart,self.yStart,self.xEnd,self.yEnd,self.border
        self.drawBlock(theme,pos,size,u,v,us,vs) # center
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]

        self.drawBlock(theme,Vec2(x,y-b),Vec2(xs,b),u,v-b,us,b) # N
        self.drawBlock(theme,Vec2(x,y+ys),Vec2(xs,b),u,v+vs,us,b) # S
        self.drawBlock(theme,Vec2(x-b,y),Vec2(b,ys),u-b,v,b,vs) # W
        self.drawBlock(theme,Vec2(x+xs,y),Vec2(b,ys),u+us,v,b,vs) # E

        self.drawBlock(theme,Vec2(x-b,y-b),Vec2(b,b),u-b,v-b,b,b) # NW
        self.drawBlock(theme,Vec2(x+xs,y+ys),Vec2(b,b),u+us,v+vs,b,b) # SE
        self.drawBlock(theme,Vec2(x-b,y+ys),Vec2(b,b),u-b,v+vs,b,b) # SW
        self.drawBlock(theme,Vec2(x+xs,y-b),Vec2(b,b),u+us,v-b,b,b) # NW

    def drawBlock(self,theme,pos,size,u,v,us,vs):
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]
        #u,v,us,vs = self.xStart,self.yStart,self.xEnd,self.yEnd
        theme.rectStreatch((x,y,xs,ys),(u,v,us,vs))

class Tiled:

    def __init__(self,xStart,yStart,xEnd,yEnd):
        self.xStart,self.yStart,self.xEnd,self.yEnd = xStart,yStart,xEnd,yEnd

    def draw(self,theme,pos,size):
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]
        z = 0
        u,v,us,vs = self.xStart,self.yStart,self.xEnd,self.yEnd
        xFit = xs/us
        yFit = ys/vs
        xPos = x
        while xFit > 0:
            yPos = y
            yFit = ys/vs
            while yFit > 0:
                fixed_us,fixed_vs = us,vs
                if xFit < 1: fixed_us = xs%us
                if yFit < 1: fixed_vs = ys%vs
                theme.rect((xPos,yPos,fixed_us,fixed_vs),(u,v))
                yPos += vs
                yFit -= 1
            xPos += us
            xFit -= 1

class TileBorder:

    def __init__(self,xStart,yStart,xEnd,yEnd,border):
        self.xStart,self.yStart,self.xEnd,self.yEnd,self.border = xStart,yStart,xEnd,yEnd,border

    def draw(self,theme,pos,size):
        u,v,us,vs,b = self.xStart,self.yStart,self.xEnd,self.yEnd,self.border
        self.drawBlock(theme,pos,size,u,v,us,vs) # center
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]

        self.drawBlock(theme,Vec2(x,y-b),Vec2(xs,b),u,v-b,us,b) # N
        self.drawBlock(theme,Vec2(x,y+ys),Vec2(xs,b),u,v+vs,us,b) # S
        self.drawBlock(theme,Vec2(x-b,y),Vec2(b,ys),u-b,v,b,vs) # W
        self.drawBlock(theme,Vec2(x+xs,y),Vec2(b,ys),u+us,v,b,vs) # E

        self.drawBlock(theme,Vec2(x-b,y-b),Vec2(b,b),u-b,v-b,b,b) # NW
        self.drawBlock(theme,Vec2(x+xs,y+ys),Vec2(b,b),u+us,v+vs,b,b) # SE
        self.drawBlock(theme,Vec2(x-b,y+ys),Vec2(b,b),u-b,v+vs,b,b) # SW
        self.drawBlock(theme,Vec2(x+xs,y-b),Vec2(b,b),u+us,v-b,b,b) # NW


    def drawBlock(self,theme,pos,size,u,v,us,vs):
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]
        z = 0
        xFit = xs/us
        yFit = ys/vs
        xPos = x
        while xFit > 0:
            yPos = y
            yFit = ys/vs
            while yFit > 0:
                fixed_us,fixed_vs = us,vs
                if xFit < 1: fixed_us = xs%us
                if yFit < 1: fixed_vs = ys%vs
                theme.rect((xPos,yPos,fixed_us,fixed_vs),(u,v))
                yPos += vs
                yFit -= 1
            xPos += us
            xFit -= 1

class TileBarX(TileBorder):
    def draw(self,theme,pos,size):
        u,v,us,vs,b = self.xStart,self.yStart,self.xEnd,self.yEnd,self.border
        self.drawBlock(theme,pos,size,u,v,us,vs) # center
        x,y = pos[0],pos[1]
        xs,ys = size[0],size[1]
        self.drawBlock(theme,Vec2(x-b,y),Vec2(b,ys),u-b,v,b,vs) # W
        self.drawBlock(theme,Vec2(x+xs,y),Vec2(b,ys),u+us+b,v,b,vs) # E

class Theme:

    TEXTURE = "data/plate.png"

    CHECKON = Stretch(360,40,20,20)
    CHECKOFF = Stretch(400,40,20,20)
    #CHECKON = Tiled(360,40,20,20)
    #CHECKOFF = Tiled(400,40,20,20)

    RADIOON = Stretch(280,40,20,20)
    RADIOOFF = Stretch(320,40,20,20)
    PANDA = Tiled(280,80,20,20)
    INPUT = TileBorder(20,300,180,180,20)
    FRAME = StretchBorder(20,300,180,180,20)
    #FORM = StretchBorder(20,20,202-20,182-20,20)
    FORM = StretchBorder(20,20,202-20,172-20,20)
    FRAMEBAR = TileBarX(280,480,140,20,20)
    BUTTON = Tiled(320,420,20,20)
    BUTTON = TileBarX(280,480,140,20,20)
    BUTTON = TileBorder(288,170,490-288,190-170,5)
    #BUTTON = Tiled(280,80,20,20)
    #BUTTON = TileBorder(20,20,202-20,182-20,20)
    DOWN = Tiled(300,160,200,40)
    TEXTCOLOR = (1,1,1,1)
    LABELCOLOR = TEXTCOLOR
    INPUTCOLOR = TEXTCOLOR

    SELECT_OPTION_COLOR = (1,0,0,1)

    VSCROLL = Stretch(470,330,10,450-330)
    VSCROLL_UP = Stretch(490,330,10,10)
    VSCROLL_CENTER = Stretch(490,370,10,40)
    VSCROLL_DOWN = Stretch(490,440,10,10)

    HSCROLL = Stretch(280,460,460-280,470-460)
    HSCROLL_UP = Stretch(280,440,10,10)
    HSCROLL_CENTER = Stretch(350,441,40,10)
    HSCROLL_DOWN = Stretch(450,440,10,10)

    SELECT_BG = StretchBorder(300,330,460-300,10,5)
    SELECT_HIGHLIGHT = StretchBorder(300,350,460-300,10,5)

    HSLIDER = TileBarX(300,369,52,10,5)
    #HSLIDER = Stretch(296,369,67,16)
    #HSLIDER = Stretch(280,460,460-280,470-460)

    WUP = Stretch(280,110,20,20)
    WDOWN = Stretch(320,110,20,20)

    X = Stretch(280,80,20,20)
    DRAG = Stretch(440,80,20,20)

    def __init__(self,texture=None):
        import __builtin__
        __builtin__.theme = self
        if texture:
            self.TEXTURE = texture
        self.texture = loader.loadTexture(self.TEXTURE)
        self.tx = float(self.texture.getXSize())
        self.ty = float(self.texture.getYSize())
        self.resetZ()
        self.first = True
        self.boxes = []

    def add(self,box):
        self.boxes.append(box)

    def rect(self,(x,y,xs,ys),(u,v)):
        us = xs
        vs = ys
        self.rectStreatch((x,y,xs,ys),(u,v,us,vs))

    def rectStreatch(self,(x,y,xs,ys),(u,v,us,vs)):
        z = 0
        color = Vec4(1,1,1,1)
        v1 = Vec3(x,z,y)
        v2 = Vec3(x+xs,z,y)
        v3 = Vec3(x+xs,z,y+ys)
        v4 = Vec3(x,z,y+ys)
        u,v,us,vs = u/self.tx,1-v/self.ty,(u+us)/self.tx,1-(v+vs)/self.ty,
        self.vertex.addData3f(v1); self.pigment.addData4f(color);   self.uv.addData2f(u,v)
        self.vertex.addData3f(v2); self.pigment.addData4f(color);   self.uv.addData2f(us,v)
        self.vertex.addData3f(v3); self.pigment.addData4f(color);   self.uv.addData2f(us,vs)
        self.vertex.addData3f(v3); self.pigment.addData4f(color);   self.uv.addData2f(us,vs)
        self.vertex.addData3f(v4); self.pigment.addData4f(color);   self.uv.addData2f(u,vs)
        self.vertex.addData3f(v1); self.pigment.addData4f(color);   self.uv.addData2f(u,v)
        self.number += 2

    def resetZ(self):
        self.z = 0

    def fixZ(self,thing):
        if thing.geom:
            thing.geom.setBin("fixed",self.z)
            self.z += 1
        if "textNode" in thing.__dict__:
            thing.textNode.setBin("fixed",self.z)
            self.z += 1

    def generate(self,box):
        vdata = GeomVertexData('shadow', GeomVertexFormat.getV3c4t2() , Geom.UHStatic)
        self.vertex = GeomVertexWriter(vdata, 'vertex')
        self.pigment = GeomVertexWriter(vdata, 'color')
        self.uv = GeomVertexWriter(vdata, 'texcoord')
        self.number = 0
        color = Vec4(1,1,1,1)
        name,pos,size,thing = box

        if not name in self.__class__.__dict__:
            return None
        drawer = self.__class__.__dict__[name]
        drawer.draw(self,pos,size)

        prim = GeomTriangles(Geom.UHStatic)
        for n in range(self.number):
            prim.addVertices(n*3,n*3+1,n*3+2)
        prim.closePrimitive()
        if self.number == 0 :
            return None
        geom = Geom(vdata)
        geom.addPrimitive(prim)

        geomnode = GeomNode('gnode')
        geomnode.addGeom(geom)

        guipart = NodePath("guisys%i"%id(self))
        guipart.setTexture(self.texture)
        guipart.attachNewNode(geomnode)
        guipart.setTransparency(True)
        guipart.setDepthWrite(False)
        guipart.setDepthTest(False)
        guipart.setTwoSided(True)
        guipart.setAttrib(LightAttrib.makeAllOff())
        guipart.setTexture(self.texture)
        guipart.setBin("fixed",0)
        return guipart

    def drawSet(self,boxes):
        vdata = GeomVertexData('shadow', GeomVertexFormat.getV3c4t2() , Geom.UHStatic)
        self.vertex = GeomVertexWriter(vdata, 'vertex')
        self.pigment = GeomVertexWriter(vdata, 'color')
        self.uv = GeomVertexWriter(vdata, 'texcoord')
        self.number = 0
        color = Vec4(1,1,1,1)

        for box in boxes:
            name,pos,size,thing = box
            if "textNode" in thing.__dict__:
                thing.textNode.setY(self.z-.001)
            if not name in self.__class__.__dict__:
                continue
            drawer = self.__class__.__dict__[name]
            drawer.draw(self,pos,size)
            #self.z -= .1
        prim = GeomTriangles(Geom.UHStatic)
        for n in range(self.number):
            prim.addVertices(n*3,n*3+1,n*3+2)
        prim.closePrimitive()
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        geomnode = GeomNode('gnode')
        geomnode.addGeom(geom)
        return geomnode

    def drawSimple(self,xs,ys,u,v,us,vs,tx,ty):
        vdata = GeomVertexData('shadow', GeomVertexFormat.getV3c4t2() , Geom.UHStatic)
        self.vertex = GeomVertexWriter(vdata, 'vertex')
        self.pigment = GeomVertexWriter(vdata, 'color')
        self.uv = GeomVertexWriter(vdata, 'texcoord')
        self.number = 0
        color = Vec4(1,1,1,1)

        x,y = 0,0
        tx,ty = float(tx),float(ty)
        z = 0
        color = Vec4(1,1,1,1)
        v1 = Vec3(x,z,y)
        v2 = Vec3(x+xs,z,y)
        v3 = Vec3(x+xs,z,y+ys)
        v4 = Vec3(x,z,y+ys)
        u,v,us,vs = u/tx,1-v/ty,(u+us)/tx,1-(v+vs)/ty,

        self.vertex.addData3f(v1); self.pigment.addData4f(color);   self.uv.addData2f(u,v)
        self.vertex.addData3f(v2); self.pigment.addData4f(color);   self.uv.addData2f(us,v)
        self.vertex.addData3f(v3); self.pigment.addData4f(color);   self.uv.addData2f(us,vs)
        self.vertex.addData3f(v3); self.pigment.addData4f(color);   self.uv.addData2f(us,vs)
        self.vertex.addData3f(v4); self.pigment.addData4f(color);   self.uv.addData2f(u,vs)
        self.vertex.addData3f(v1); self.pigment.addData4f(color);   self.uv.addData2f(u,v)
        self.number += 2

        prim = GeomTriangles(Geom.UHStatic)
        for n in range(self.number):
            prim.addVertices(n*3,n*3+1,n*3+2)
        prim.closePrimitive()
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        geomnode = GeomNode('gnode')
        geomnode.addGeom(geom)
        return NodePath(geomnode)


    def draw(self):
        self.resetZ()

