from panda3d.core import *
from missionBase import missionBase

class mission(missionBase):

    def __init__(self):
        missionBase.__init__(self)
    
    def load(self):
        self.loadTerrain()
        #self.playMusic()
        #self.loadLevel()
        self.loadSky()
        self.loadFog()
        #self.loadLights()
        
        # This thing
        # Some camera stuff
        base.setBackgroundColor(.2, .8, .2)
        base.camLens.setFov(75)
        
        base.jumpSound = loader.loadSfx("resources/sound/jump.wav")
        
    def loadTerrain(self):
        # Terrain
        # Oh snap!
        terrain = GeoMipTerrain("LevelTerrain")
        root = terrain.getRoot()
        terrain.setHeightfield("missions/200px-Heightmap.png")
        root.reparentTo(base.lightable)
        root.setPos(-150, -150, 0)
        
        self.tertex = loader.loadTexture('resources/textures/OmahaRock.jpg')
        
        ts = TextureStage('ts')
        root.setTexture(ts, self.tertex)
        root.setTexScale(ts,VBase2(32,32))
        
        root.setSz(35)
        terrain.setBruteforce(True)
        
        base.terrain = terrain
        base.terrain.generate()
        
    
    def playMusic(self):
        # myusic
        sound = loader.loadSfx("resources/music/Discipline.mp3")
        sound.setLoop(True)
        
        sound.play()
        #sound.setPlayRate(-1)

    def loadSky(self):
        # Good God that was hard as factor
        base.sky = loader.loadModel('resources/models/skybox 1/skybox')
        base.sky.setScale(100)
        base.sky.setBin('background', 0)
        base.sky.setDepthWrite(0)
        base.sky.setTwoSided(True)
        base.sky.reparentTo(render)
        base.sky.clearLight(base.plnp)
    
    def loadLevel(self):
        """ load the self.level 
            must have
            <Group> *something* { 
              <Collide> { Polyset keep descend } 
            in the egg file
        """
        self.level = loader.loadModel('resources/models/level')
        self.level.reparentTo(render)
        self.level.setTwoSided(True)
    
    def loadFog(self):
        #Create an instance of fog called 'distanceFog'.
        #'distanceFog' is just a name for our fog, not a specific type of fog.
        self.fog = Fog('distanceFog')
        #Set the initial color of our fog to black.
        self.fog.setColor(0, 0, 0)
        #Set the density/falloff of the fog.  The range is 0-1.
        #The higher the numer, the "bigger" the fog effect.
        self.fog.setExpDensity(.08)
        #We will set fog on render which means that everything in our scene will
        #be affected by fog. Alternatively, you could only set fog on a specific
        #object/node and only it and the nodes below it would be affected by
        #the fog.
        render.setFog(self.fog)
    
    def loadLights(self):
        # Now we create a directional light. Directional lights add shading from a
        # given angle. This is good for far away sources like the sun
        self.directionalLight = render.attachNewNode( DirectionalLight( "directionalLight" ) )
        self.directionalLight.node().setColor( Vec4( .35, .35, .35, 1 ) )
        # The direction of a directional light is set as a 3D vector
        self.directionalLight.node().setDirection( Vec3( 1, 1, -2 ) )
        # These settings are necessary for shadows to work correctly
        self.directionalLight.setZ(60)
        dlens = self.directionalLight.node().getLens()
        dlens.setFilmSize(41, 21)
        dlens.setNearFar(50, 75)
        #self.directionalLight.node().showFrustum()