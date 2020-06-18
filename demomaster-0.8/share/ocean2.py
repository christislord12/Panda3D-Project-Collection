import demobase, geomutil

from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Plane
from pandac.PandaModules import PlaneNode
from pandac.PandaModules import PStatClient
from pandac.PandaModules import CullFaceAttrib
from pandac.PandaModules import RenderState
from pandac.PandaModules import ShaderAttrib, TransparencyAttrib,TexGenAttrib

class WaterNode(demobase.Att_base):
    def __init__(self, width, height, segmentX, segmentY, z, useCubemapOnly=False, debug=False):
        demobase.Att_base.__init__(self, False, "Ocean2")

        self.useCubemapOnly = useCubemapOnly
        self.debug = debug

        # Water surface
        #self.waterNP = geomutil.makeEggPlane(width, height, segmentX, segmentY)
        self.waterNP = geomutil.createPlane('water', width, height, segmentX, segmentY)
        self.waterNP.setTransparency(TransparencyAttrib.MAlpha )
        self.waterNP.reparentTo(render)

        self.waterNP.setPos(0,0,z)
        if debug:
            shaderfile = 'shaders/ocean2_debug.sha'
        elif useCubemapOnly:
            shaderfile = 'shaders/ocean2_cubemap.sha'
        else:
            shaderfile = 'shaders/ocean2.sha'

        self.waterNP.setShader(loader.loadShader( shaderfile ))

        if not useCubemapOnly:
            # Reflection plane
            self.waterPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z+20 ) )

            planeNode = PlaneNode( 'waterPlane' )
            planeNode.setPlane( self.waterPlane )
            # Buffer and reflection camera
            self.buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
            self.buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )

            cfa = CullFaceAttrib.makeReverse( )
            rs = RenderState.make(cfa)

            self.watercamNP = base.makeCamera( self.buffer )
            self.watercamNP.reparentTo(render)
            #sa = ShaderAttrib.make()
            #sa = sa.setShader(loader.loadShader('shaders/splut3Clipped.sha') )

            self.cam = self.watercamNP.node()
            self.cam.getLens( ).setFov( base.camLens.getFov( ) )
            self.cam.getLens().setNear(1)
            self.cam.getLens().setFar(5000)
            self.cam.setInitialState( rs )
            #self.cam.setTagStateKey('Clipped')
            #self.cam.setTagState('True', RenderState.make(sa))


            # ---- water textures ---------------------------------------------
            # reflection texture, created in realtime by the 'water camera'
            tex0 = self.buffer.getTexture( )
            tex0.setWrapU(Texture.WMClamp)
            tex0.setWrapV(Texture.WMClamp)
            ts0 = TextureStage( 'reflection' )
            self.waterNP.setTexture( ts0, tex0 )

        self.cubemap_mode = True
        # distortion texture
        tex1 = loader.loadTexture('textures/waves200.tga')
        ts1 = TextureStage('distortion')
        self.waterNP.setTexture(ts1, tex1)

        if debug:
            # this texture is just for debugging
            ts2 = TextureStage('debug')
            tex2 = loader.loadTexture('textures/colorplate.png') # a color texture for debugging
            self.waterNP.setTexture(ts2, tex2)

        # texture stage for cube map
        self.ts3 = TextureStage('environ')

        self.changeCameraPos(Vec3(0,0,0))

    def setCubeMap(self, cubemapfile):
        tex = loader.loadCubeMap(cubemapfile)
        tex.setMinfilter( Texture.FTLinearMipmapLinear ) # for reflection blur to work
        self.waterNP.clearTexture(self.ts3)
        self.waterNP.setTexGen(self.ts3, TexGenAttrib.MEyeCubeMap)
        self.waterNP.setTexture(self.ts3, tex)

    def setFov(self, fov):
        # the reflection cam has to follow the base.cam fov
        if not self.useCubemapOnly:
            self.cam.getLens().setFov(fov)

    def Destroy(self):
        #shader = self.waterNP.getShader()
        self.waterNP.clearShader()
        if not self.useCubemapOnly:
            base.graphicsEngine.removeWindow(self.buffer)
            self.cam.setInitialState(RenderState.makeEmpty())
            self.watercamNP.removeNode()
        #self.waterNP.clearTexture()
        self.waterNP.removeNode()


    def changeCameraPos(self, pos, mc=None):
        if mc != None and not self.useCubemapOnly:
            # update matrix of the reflection camera
            mf = self.waterPlane.getReflectionMat( )
            self.watercamNP.setMat(mc * mf)

        mypos = self.waterNP.getPos()
        pos -= mypos
        self.waterNP.setShaderInput('eyePosition', Vec4(pos[0],pos[1],pos[2],0))
        #pos = base.camera.getPos()
        #self.waterNP.setShaderInput('eyePosition', Vec4(pos[0],pos[1],pos[2],0))
        #self.waterNP.setShaderInput('eyePosition', base.camera)
        #self.waterNP.setShaderInput('eyePosition', self.dummy)

    def setParams(self,
        waveFreq, waveAmp,
        speed0, speed1,
        bumpScale, bumpSpeed,textureScale,
        reflectionAmount, waterAmount,
        deepcolor, shallowcolor,reflectioncolor,
        fresnelPower, fresnelBias, hdrMultiplier,reflectionBlur,
        debuglevel=0, debuginfo=None):
        if self.cubemap_mode or self.useCubemapOnly:
            cubemap = 1.0
        else:
            cubemap = 0.0
        self.waterNP.setShaderInput('waveInfo', Vec4( waveFreq, waveAmp, bumpScale,0 ))
        self.waterNP.setShaderInput('param2', Vec4( bumpSpeed[0], bumpSpeed[1], textureScale[0], textureScale[1] ))
        self.waterNP.setShaderInput('param3', Vec4( reflectionAmount, waterAmount, debuglevel, cubemap))
        self.waterNP.setShaderInput('param4', Vec4( fresnelPower, fresnelBias, hdrMultiplier, reflectionBlur))
        self.waterNP.setShaderInput('speed', Vec4( speed0[0], speed0[1], speed1[0], speed1[1]))
        if self.debug:
            self.waterNP.setShaderInput('debug', debuginfo)
        self.waterNP.setShaderInput('deepcolor', deepcolor)
        self.waterNP.setShaderInput('shallowcolor', shallowcolor)
        self.waterNP.setShaderInput('reflectioncolor', reflectioncolor)

        #self.waterNP.setShaderInput('waterdistort', Vec4( offset, strength, refractionfactor, refractivity ))
        #self.waterNP.setShaderInput('wateranim', Vec4( vx, vy, scale, 0 )) # vx, vy, scale, skip

    # call this method to get standard attributes for wx interface control
    def setStandardControl(self):
        self.att_waveFreq = demobase.Att_FloatRange(False, "Wave Freq", 0.0, 0.05, 0.028, 3)
        self.att_waveAmp = demobase.Att_FloatRange(False, "Wave Amp", 0.0, 25.0, 1.8, 2)
        self.att_waveSpeed0 = demobase.Att_Vecs(False,"Wave 0 Speed",2,(-1,0), -5, 5)
        self.att_waveSpeed1 = demobase.Att_Vecs(False,"Wave 1 Speed",2,(-0.7,0.7), -5, 5)
        self.att_bumpScale = demobase.Att_FloatRange(False, "Bump Scale", 0.0, 2.0, 0.2, 2)
        self.att_bumpSpeed = demobase.Att_Vecs(False,"Bump Speed",2,(0.015,0.005), -0.1, 0.1)
        self.att_textureScale = demobase.Att_Vecs(False,"Texture Scale",2,(25.0,25.0), 0.0, 40.0, 0)

        self.att_fresnelPower = demobase.Att_FloatRange(False, "Fresnel Power", 0.0, 10.0, 5.0)
        self.att_fresnelBias = demobase.Att_FloatRange(False, "Fresnel Bias", 0.0, 1.0, 0.328)
        self.att_hdrMultiplier = demobase.Att_FloatRange(False, "HDR Multiplier", 0.0, 2.0, 0.471)
        self.att_reflectionBlur = demobase.Att_FloatRange(False, "Reflection Blur", 0.0, 10.0, 0.0)

        self.att_reflectionAmount = demobase.Att_FloatRange(False, "Relection Amount", 0.0, 1.0, 1.0)
        self.att_waterAmount = demobase.Att_FloatRange(False, "Water Amount", 0.0, 1.0, 0.3)
        if self.debug:
            self.att_debuglevel = demobase.Att_IntRange(False, "Debug Level", 0, 10, 0)
            self.att_debug = demobase.Att_Vecs(False,"Debug Info",4,(0.0,0.0,0.0,0.0), -1000.0, 1000.0, 2)

        self.att_deepcolor = demobase.Att_color(False, "Deep Water Color", Vec4(0.0,0.3,0.5,1.0))
        self.att_shallowcolor = demobase.Att_color(False, "Shallow Water Color", Vec4(0.0,1.0,1.0,1.0))
        self.att_reflectioncolor = demobase.Att_color(False, "Reflection Color", Vec4(0.95,1.0,1.0,1.0))

        self.att_waveFreq.setNotifier(self.changeParams)
        self.att_waveAmp.setNotifier(self.changeParams)
        self.att_waveSpeed0.setNotifier(self.changeParams)
        self.att_waveSpeed1.setNotifier(self.changeParams)

        self.att_bumpScale.setNotifier(self.changeParams)
        self.att_bumpSpeed.setNotifier(self.changeParams)
        self.att_textureScale.setNotifier(self.changeParams)

        self.att_fresnelPower.setNotifier(self.changeParams)
        self.att_fresnelBias.setNotifier(self.changeParams)
        self.att_hdrMultiplier.setNotifier(self.changeParams)
        self.att_reflectionBlur.setNotifier(self.changeParams)

        self.att_reflectionAmount.setNotifier(self.changeParams)
        self.att_waterAmount.setNotifier(self.changeParams)
        if self.debug:
            self.att_debuglevel.setNotifier(self.changeParams)
            self.att_debug.setNotifier(self.changeParams)

        self.att_deepcolor.setNotifier(self.changeParams)
        self.att_shallowcolor.setNotifier(self.changeParams)
        self.att_reflectioncolor.setNotifier(self.changeParams)

        self.changeParams(None)

    def changeParams(self, object):
        if self.debug:
            debuglevel = self.att_debuglevel.v
            debuginfo = self.att_debug.getValue()
        else:
            debuglevel = 0
            debuginfo = None
        self.setParams(
                self.att_waveFreq.v, self.att_waveAmp.v,
                self.att_waveSpeed0.getValue(),self.att_waveSpeed1.getValue(),
                self.att_bumpScale.v,self.att_bumpSpeed.getValue(), self.att_textureScale.getValue(),
                self.att_reflectionAmount.v,self.att_waterAmount.v,
                self.att_deepcolor.getColor(),self.att_shallowcolor.getColor(),self.att_reflectioncolor.getColor(),
                self.att_fresnelPower.v, self.att_fresnelBias.v, self.att_hdrMultiplier.v,self.att_reflectionBlur.v,
                debuglevel, debuginfo)

    def hide(self):
        self.waterNP.hide()

    def show(self):
        self.waterNP.show()
