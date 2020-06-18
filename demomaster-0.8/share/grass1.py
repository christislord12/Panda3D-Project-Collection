
from random import randint, random
import math, sys
import demobase, geomutil

from pandac.PandaModules import Filename

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2
from pandac.PandaModules import Shader, Texture, TextureStage


class LeafModel():
    def __init__(self, name, nrplates, width, height, shaderfile, texturefile, uvlist, jitter=-1):
        maker = CardMaker( 'leaf' )
        maker.setFrame( -width/2.0, width/2.0, 0, height)
        #maker.setFrame( 0,1,0,1)
        np = NodePath('leaf')
        for i in range(nrplates):
            if uvlist != None:
                maker.setUvRange(uvlist[i][0],uvlist[i][1])
            else:
                maker.setUvRange(Point2(0,0),Point2(1,0.98))
            node = np.attachNewNode(maker.generate())
            #node.setTwoSided( True )
            node.setHpr(i * 180.0 / nrplates,0,0)
        np.flattenStrong()
        #np.flattenLight()
        #np.setTwoSided( True )
        self.name = name
        self.texturefile = texturefile
        self.shaderfile = shaderfile
        self.np = np
        if jitter == -1:
            self.jitter = height/width/2
        else:
            self.jitter = jitter


class GrassNode(demobase.Att_base):
    def __init__(self, name, parentnode=render, texture= 'textures/grassPack.png', color=None ):
        demobase.Att_base.__init__(self, False,name=name)

        #self.att_grassDistance = demobase.Att_FloatRange(False,"Clip Distance",0,grassDistance*2,grassDistance,0);
        #self.setNotifier(self.changeParams)
        if color != None:
            self.att_color = demobase.Att_color(False, "Color", color)
            self.color = True
            self.att_color.setNotifier(self.changecolor)
        else:
            self.color = False

        self.tex = None
        self.parentnode = parentnode

        # Auxiliary clip plane
        #clipPlane = Plane( Vec3( 0, -1, 0 ), Point3( 0, grassDistance, 0 ) )
        #clipNode = PlaneNode( 'clipPlane' )
        #clipNode.setPlane( clipPlane )
        #clipNP = base.camera.attachNewNode( clipNode )
        #self.clipNP = clipNP

        self.grassNP = None
        #self.reset()

    def reset(self):
        if self.grassNP != None:
            self.grassNP.clearShader()
            self.grassNP.removeNode()

        self.grassNP = self.parentnode.attachNewNode("grass")
        self.grassNP.setPos( 0, 0, 0 )
        if self.tex != None:
            self.grassNP.setTexture( self.tex )
        self.grassNP.setTwoSided( True )
        self.grassNP.setTransparency( TransparencyAttrib.MAlpha )
        #self.grassNP.setTransparency( TransparencyAttrib.MMultisample )
        self.grassNP.setDepthWrite( False )
        self.grassNP.setShader( loader.loadShader( self.model.shaderfile ) )
        self.grassNP.setShaderInput( 'grass', Vec4(0,0,0,0))

        #self.grassNP.setClipPlane( self.clipNP )
        if self.color:
            self.changecolor(None)

##    def addGrass(self, pos, heading, path = 'models/grass.egg'):
##        np = loader.loadModel( path )
##        np.reparentTo( self.grassNP )
##        np.setPos(pos)
##        #np.setHpr(Vec3(heading,0,0))
##        return np

    def setModel(self, model):
        self.model = model
        tex = loader.loadTexture(model.texturefile)
        tex.setMinfilter( Texture.FTLinearMipmapLinear )
        tex.setMagfilter( Texture.FTLinearMipmapLinear )
        tex.setAnisotropicDegree(2)

        self.tex = tex


    def addGrassWithModel(self, pos, heading):
        np = self.model.np.copyTo( self.grassNP )
        #np = self.model.instanceTo( self.grassNP )
        #np = loader.loadModel( 'models/grass.egg' )
        #np.reparentTo(self.grassNP)

        np.setTwoSided( True )
        np.setHpr(Vec3(heading,0,0))
        np.setPos(pos)
        return np

    def Destroy(self):

        self.grassNP.clearShader()
        self.grassNP.removeNode()

    #def changeParams(self):
    #    pass

    def setTime(self, time):
        # Grass jitter
        dx  = 1.8 * math.sin( time * 1.6 )
        dx += 2.1 * math.sin( time * 0.5 )
        dx += 2.6 * math.sin( time * 0.1 )
        dx *= self.model.jitter
        #self.grassNP.setShaderInput( 'grass', Vec4(dx,dx,0,self.att_grassDistance.v))
        self.grassNP.setShaderInput( 'grass', Vec4(dx,dx,0,0))

    def flatten(self):
        #self.grassNP.flattenLight()
        self.grassNP.flattenMedium()
        #self.grassNP.flattenStrong()

    def changecolor(self, object):
        self.grassNP.setShaderInput( 'ambient', self.att_color.getColor())

    def setColor(self, color):
        if self.grassNP:
            if hasattr(self, 'att_color'):
                self.att_color.setColor(color)
            else:
                self.grassNP.setShaderInput( 'ambient', color)

    def setShaderInfo(self, grasscolor,light,lightcolor,attenuation):
        self.grassNP.setShaderInput('ambient', grasscolor)
        self.grassNP.setShaderInput('light', light)
        self.grassNP.setShaderInput('lightcolor', lightcolor)
        self.grassNP.setShaderInput('attenuation', attenuation[0],attenuation[1],attenuation[2],0 )
