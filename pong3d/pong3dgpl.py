# -*- coding: utf-8 -*-
"""
3dpong gameplay module - see __main__ section for demo usage

Gameplay: press SPACEBAR to launch the ball, move the mouse or use the WASD or the arrow keys or even the joystick to move the pad. A game is won by the player who  wins 2 sets more than his foe. Each set is won by the player who wons 3 rallies but gotta win 2 rallies more than his foe in case of tie score.
@author: fabius
@copyright: fabius@2010
@license: GCTA give credit to (the) authors
@version: 0.1
@date: 2010-09
@contact: astelix (U{panda3d forums<http://www.panda3d.org/forums/profile.php?mode=viewprofile&u=752>})
@status: eternal WIP

"""
import random, sys, time
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from gamelogic01 import gameplaybase
try:
  from easyinput import *
  _EASYINPUT=True
except ImportError: _EASYINPUT=False

#=========================================================================
#
class gameplay(gameplaybase):
  """ Pong3D gameplay class. Derived from a generic base gameply class, this is custom-specialized to play the pong3D game.
  """
  _DEBUG=False
  PADVEL=1.
  CPUSPD=.15
  NPCSPD=PADVEL
  BALLSPEED=1.0
  BALLSPEEDMAX=2.0
  _CPUPAD=0
  _HUMANPAD=1
  _SETTINGS={
    #MODES: '2d','3d','3dg'
    'mode': '3dg',
    'opponent': 'human',
    'games': 3,
    'sets': 3,
    'maxfoes': 4,
    'playernames': ['CPU0', 'Player1']
  }
  _SCOREPOINTS={
    'rallyunit': 4,
    'bonusunit': 100,
    'penaltyunit': 10,
  }
  #-----------------------------------------------------
  #
  def setcamera(self):
    """ WARNING you actually cannot dynamically switch from 2d to 3d and vice-versa but just stay stick to one dimension or the other one
    """
    if self._SETTINGS['mode'].lower().startswith('3d'):
      # Choose a suitable pair of colors for the left and right eyes
      leftColor = ColorWriteAttrib.CRed
      rightColor = ColorWriteAttrib.CBlue | ColorWriteAttrib.CGreen
      # Enable anaglyph stereo mode on the window
      base.win.setRedBlueStereo(True, leftColor, rightColor)
      # Remove the original, mono DisplayRegion
      oldDr = base.cam.node().getDisplayRegion(0)
      oldDr.setCamera(NodePath())
      # Create a new, stereo DisplayRegion
      dr = base.win.makeStereoDisplayRegion()
      dr.setCamera(base.cam)
      # The stereo region draws the left eye, then the right eye.  We need
      # to clear the depth buffer after drawing the left eye and before
      # drawing the right eye.
      dr.getRightEye().setClearDepthActive(True)
      base.camLens.setInterocularDistance(0.339)

      if self._SETTINGS['mode'].lower() == '3dg':
        dr.setStereoChannel(Lens.SCStereo)
      else: dr.setStereoChannel(Lens.SCMono)

      self.parent.cam.setPos(-25,-15,0)
      self.parent.cam.lookAt(self.field)
      self.parent.cam.setR(90)
    else:
      lens = OrthographicLens()
      lens.setFilmSize(20, 15)
      self.parent.cam.node().setLens(lens)
      self.parent.cam.setY(-2)

  #-----------------------------------------------------
  #
  def setinputs(self):
    if _EASYINPUT: self.si_easyinput()
    else: self.si_noeasyinput()
    self.parent.disableMouse()
    if self._DEBUG:
      self.accept('c', self.toggle_collisions)
      self.accept('x', self.parent.toggleWireframe)
      self.accept('o', self._setiod,[1])
      self.accept('p', self._setiod,[-1])
      self.accept('l', self._setcvd,[1])
      self.accept('k', self._setcvd,[-1])
      base.setFrameRateMeter(True)

  def si_noeasyinput(self):
    def accepad(ks, p, v):
      """ ease the pad key controls input setup """
      for k in ks:
        self.accept(k, self.setpadvel, [p, v])
        self.accept('%s-up'%k, self.setpadvel, [p, 0])
        v=-v
    #
    if self._SETTINGS['mode'].lower().startswith('3d'):
      keys=[['a', 'd'],['arrow_left', 'arrow_right']]
    else: keys=[['w', 's'],['arrow_up', 'arrow_down']]
    if self._SETTINGS['opponent'] <> "cpu":
      self._SETTINGS['playernames']=['Player1','Player2']
      accepad(keys[0], 0, self.PADVEL)
    accepad(keys[1], 1, self.PADVEL)

  def si_easyinput(self):
    #
    cfg=""
    ibridge={}
    if self._SETTINGS['mode'].lower().startswith('3d'):
      cfg+="""
bind a "pad0up"
bind d "pad0down"
bind arrow_up ""
bind arrow_down ""
bind arrow_left "pad1up"
bind arrow_right "pad1down"
bind mouse-x "mousemove"
"""
    else:
      cfg+="""
bind w "pad0up"
bind s "pad0down"
bind arrow_up "pad1up"
bind arrow_down "pad1down"
bind arrow_left ""
bind arrow_right ""
"""
    if self._SETTINGS['opponent'] <> "cpu":
      ibridge['pad0up']=lambda v,p=0: self.xsetpadvel(p,v)
      ibridge['pad0down']=lambda v,p=0: self.xsetpadvel(p,-v)
    else:
      ibridge['heading']=lambda v,p=0: self.xsetpadvel(p,v)
    ibridge['pad1up']=lambda v,p=1: self.xsetpadvel(p,v)
    ibridge['pad1down']=lambda v,p=1: self.xsetpadvel(p,-v)
    ibridge['mousemove']=lambda v,p=1: self.xsetpadvel(p,-v)

    self.xinput=easyinput(cfg, ibridge, debug=False)

  def xsetpadvel(self,a,b):
    self.setpadvel(a,b)

  def _setiod(self, v=0):
    d=.05
    v=base.camLens.getInterocularDistance()+(v*d)
    base.camLens.setInterocularDistance(v)
    self.dbgprint("IOD:%r"%base.camLens.getInterocularDistance())
  def _setcvd(self, v=0):
    d=.1
    v=base.camLens.getConvergenceDistance()+(v*d)
    base.camLens.setConvergenceDistance(v)
    self.dbgprint("CVD:%r"%base.camLens.getConvergenceDistance())

  #-----------------------------------------------------
  #
  def setscene(self):
    if self._SETTINGS['opponent'] <> "cpu":
      self._SETTINGS['playernames']=['Player1','Player2']
    #
    self.field=loader.loadModel('pong3d')
    self.field.setScale(10)
    self.field.reparentTo(self.parent.render)
    self.parent.cam.lookAt(self.field)
    #
    self.lights=[]
    # Create Ambient Light
    lv=.3
    ambientLight = AmbientLight('ambientLight')
    ambientLight.setColor(Vec4(lv, lv, lv, 1))
    ambientLightNP = self.parent.render.attachNewNode(ambientLight)
    self.lights.append(ambientLightNP)
    self.parent.render.setLight(ambientLightNP)
    # Directional light 01
    lpos=(-4, -6, 2)
    lv=.7
    directionalLight = DirectionalLight('directionalLight')
    directionalLight.setColor(Vec4(lv, lv, lv, 1))
    directionalLightNP = self.parent.render.attachNewNode(directionalLight)
    directionalLightNP.setPos(lpos)
    directionalLightNP.lookAt(self.field)
    self.lights.append(directionalLightNP)
    self.parent.render.setLight(directionalLightNP)

    font=loader.loadFont("data/fonts/slkscre.ttf")
    font.setMagfilter(Texture.FTNearest)
    self.text={
      'score': OnscreenText(fg=(1,1,1,1), font = font,
        text = '', pos = (0, .75), scale = 0.3, mayChange=True,
      ),
      'sets': OnscreenText(fg=(1,1,1,1), font = font,
        text = '', pos = (0, .65), scale = 0.08, mayChange=True,
      ),
      'cmsg': OnscreenText(fg=(1,1,1,1), font = font,
        text = '', pos = (.0, .0), scale = 0.3, mayChange=True,
      ),
    }

  #-----------------------------------------------------
  #
  def setgame(self):
    self.pad=[]
    for i in range(2):
      self.pad.append({})
      self.pad[i]['name']=self._SETTINGS['playernames'][i]
      self.pad[i]['totrly']=0
      self.pad[i]['totgam']=0
      self.pad[i]['gam']=0
      self.pad[i]['set']=0
      self.pad[i]['vel']=0
      self.pad[i]['mdl']=self.field.find("**/pad%d"%i)
      self.pad[i]['mdl'].setBin('fixed', 40)

    self._collphysetup()
    # n items deve corrispondere a maxfoes+1
    self._BOTS=[self.bot0, self.bot0, self.bot1, self.bot1, self.bot1]
    self.actualbot=self._BOTS[0]

    self.maintask = None
    self.npctask=None
    self.setmaintask(1)

    self.playerturn=random.choice(range(2))
    self.updatescore()
    self.ballreset()

  #-----------------------------------------------------
  #
  def setmaintask(self, on):
    if on:
      if not self.maintask:
        self.maintask = taskMgr.add(self.mainloop, "gpl01_main", priority = 35)
        self.maintask.last = 0
        if self._SETTINGS['opponent'] == "cpu":
          self.npctask = taskMgr.doMethodLater(self.CPUSPD, self.npcloop, 'gpl01_npctsk')
        else: self.npctask=None
    else:
      if self.maintask:
        taskMgr.remove(self.maintask)
        self.maintask=None
        if self._SETTINGS['opponent'] == "cpu": taskMgr.remove(self.npctask)

  #-----------------------------------------------------
  #
  def onfinish(self):
    self.xinput.finish()
    self.parent.physicsMgr.clearPhysicals()
    self.parent.cTrav.clearColliders()
    self.field.removeNode()
    for t in self.text: self.text[t].destroy()
    for l in self.lights: self.parent.render.clearLight(l)

  #-----------------------------------------------------
  #
  def mainloop(self, task):
    dt = task.time - task.last
    task.last = task.time
    for i in range(2):
      padvel=self.pad[i]['vel']
      if padvel:
        pad=self.pad[i]['mdl']
        z=pad.getZ()+(padvel*dt)
        z=max(min(z, self.PADLIMZ), -self.PADLIMZ)
        pad.setZ(z)
    # check ball off the wall boundaries
    if (
      (abs(self.ball.getPosition()[2]) > .75) or
      (abs(self.ball.getPosition()[0]) > 1.08)
    ):
      self.playerscore(self.ball.getPosition()[0] > 0)
    return task.cont

  #-----------------------------------------------------
  #
  def _centerpad(self, padz):
    v=0.
    if abs(padz) > random.uniform(.0, .06): v=-1. if padz > 0. else 1.
    return v

  #-----------------------------------------------------
  #
  def bot0(self, padz, ballpos, balldir):
    """ npc AI (actually very dumb) """
    bpx,bpy,bpz=ballpos
    v=0.
    # bpx > 0. = dentro metacampo pad0
    #if bpx > .35/self.BALLSPEED:
    if bpx > .0:
      if (abs(bpz-padz) > .08) and (abs(bpz) < .65):
        v=1. if bpz > padz else -1.
    else: v=self._centerpad(padz)
    return v

  #-----------------------------------------------------
  #
  def bot1(self, padz, ballpos, balldir):
    """ npc AI (less dumb) """
    bpx,bpy,bpz=ballpos
    balldirz=balldir[2]
    v=0.
    if bpx > 0.:
      d=.5/self.BALLSPEED
      self.dbgprint("[CPU1]rot:%0.3f lim: %0.3f bpx:%0.3f"%(balldirz, d, bpx))
      if bpx < d:
        self.dbgprint("...centering")
        if abs(balldirz) > .003: return self._centerpad(padz)
      if (abs(bpz-padz) > .08) and (abs(bpz) < .65):
        v=1. if bpz > padz else -1.
        self.dbgprint("...following")
    else: v=self._centerpad(padz)
    return v

  #-----------------------------------------------------
  #
  def npcloop(self, task):
    pv=self.actualbot(
      self.pad[0]['mdl'].getZ(),
      self.ball.getPosition(),
      self.ball.getImplicitVelocity()
    )
    self.setpadvel(0, pv*self.PADVEL*self.CPUSPD*6.)
    return task.again

  #-----------------------------------------------------
  #
  def _collphysetup(self):
    self.parent.cTrav=CollisionTraverser()
    self.parent.cTrav.setRespectPrevTransform(True)
    self.parent.enableParticles()
    self.collisionHandler = PhysicsCollisionHandler()

    ballmodel=self.field.find("**/ball")
    self.ballNP=self.field.attachNewNode(PandaNode("phball"))
    ballAN=ActorNode("ballactnode")
    ballANP=self.ballNP.attachNewNode(ballAN)
    ballmodel.reparentTo(ballANP)
    ballCollider = ballmodel.find("**/ball_collide")
    self.collisionHandler.addCollider(ballCollider, ballANP)
    self.parent.cTrav.addCollider(ballCollider, self.collisionHandler)
    self.collisionHandler.addInPattern('ball-into-all')
    self.accept('ball-into-all', self.collideEventIn)
    self.parent.physicsMgr.attachPhysicalNode(ballAN)
    # NOTE we'll drive the ball from the PhysicsObject
    self.ball=self.ballNP.getChild(0).node().getPhysicsObject()
    #!!!
    ###self.ball.setOriented(True)

  #-----------------------------------------------------
  #
  def collideEventIn(self, entry):
    intoNP=entry.getIntoNodePath()
    vec=entry.getSurfaceNormal(intoNP)
    #the ball hit a pad
    if intoNP.getName().startswith("pad"):
      #tweak the pad hit bounce speed
      vec=vec*self.BALLSPEED*1.5
      self.wallbouncheck(reset=True)
      padi=int(intoNP.getName()[3])
      self.pad[padi]['totrly']+=1
      self.playeffect('pad%d'%padi)
    # ball's walls bounce
    else:
      wbc=self.wallbouncheck()
      if  wbc <> None: return self.playerscore(wbc)
      else: vec=vec+self.ball.getVelocity()
      self.playeffect('borderhit')
    vec*=self.BALLSPEED
    self.ballinpulse(vec=Vec3(vec.getX(), 0, vec.getZ()))

  #-----------------------------------------------------
  #
  def updatescore(self):
    self.text['score'].setText('%0d   %0d'%(
        self.pad[1]['gam'], self.pad[0]['gam']
      )
    )
    self.text['sets'].setText('%s: %0d      %s: %0d'%(
        self.pad[1]['name'], self.pad[1]['set'],
        self.pad[0]['name'], self.pad[0]['set'],
      )
    )

  #-----------------------------------------------------
  #
  foesdefeated=0
  totsets=0
  def endset(self):
    """ a set is won by one player """
    self.playeffect('applause_1')

    won=self.pad[1]['gam'] > self.pad[0]['gam']
    self.dbgprint(">> END OF GAME - won by player %d"%won)
    self.pad[0]['gam']=0
    self.pad[1]['gam']=0
    self.pad[won]['set']+=1
    self.totsets+=1

    # at each game the ball speed will increase (until BALLSPEEDMAX)
    if self.BALLSPEED < self.BALLSPEEDMAX: self.BALLSPEED*=1.05
    self.BALLSPEED = min(self.BALLSPEED, self.BALLSPEEDMAX)
    self.dbgprint(">> BALLSPEED increased to %0.2f"%self.BALLSPEED)

    # a set is won reaching the games limit self._SETTINGS['games'] but also exceeding the other score by 2 points, e.g.: 6-0 won but 6-5 keep going
    if (
      self.pad[won]['set'] >= ((self._SETTINGS['sets']/2)+1)
      and (abs(self.pad[0]['set'] - self.pad[1]['set'])) >= 2
    ):
      # if human wins and foe is' CPU, the game keep going increasing the cpu foe bravura and shortening the pad size, otherwise game over.
      if (
        (self.pad[1]['set'] > self.pad[0]['set'])
        and (self._SETTINGS['opponent'] == 'cpu')
      ):
        self.intermessage(
          "%s defeated!\nHere come another"%self.pad[0]['name'], delay=3
        )
        self.dbgprint(">>> %s defeated" % self.pad[0]['name'])
        self.foesdefeated+=1
        self.pad[0]['name']="CPU%d"%self.foesdefeated
        self.pad[0]['set']=0
        self.pad[1]['set']=0
        if self.foesdefeated <= self._SETTINGS['maxfoes']:
          self.PADVEL+=.5
          self.actualbot=self._BOTS[self.foesdefeated]
          for i in range(2):
            # riduzione delle dim dei pad: a maxfoes viene ridotto di un 60% e la riduzione e' quindi proporzionale ai maxfoes ad ogni foe sconfitto
            psz=self.pad[i]['mdl'].getSz()
            dsz=60./self._SETTINGS['maxfoes']
            self.pad[i]['mdl'].setSz(psz-(psz*dsz/100))
            #recalc pad range
            b=self.pad[1]['mdl'].getTightBounds()
            w,n,h=b[1]-b[0]
            self.PADLIMZ=.7-(h/2.)
        self.ballreset()
      else: self.gameover()
    else:
      self.ballreset()
      self.intermessage("Set won by\n%s"%self.pad[won]['name'], delay=3)
    self.updatescore()

  #-----------------------------------------------------
  #
  def intermessage(self, msg, scale=.1, delay=-1):
    self.text['cmsg'].hide()
    if msg and type(msg) == str:
      self.text['cmsg'].setScale(scale)
      self.text['cmsg'].setText(msg)
      self.text['cmsg'].setPos(0,0)
      self.text['cmsg'].show()
    if delay > 0:
      taskMgr.doMethodLater(delay, self.intermessage, 'gpl01_intmsg')
    return None

  #-----------------------------------------------------
  #
  def gameover(self):
    self.setmaintask(0)
    self.ballNP.hide()
    self.dbgprint("GAME  OVER!")
    seq=Sequence()
    won=self.pad[1]['set'] > self.pad[0]['set']

    if self._SETTINGS['opponent'] == 'human':
      wonmsg="Game won by\n'%s'"%self.pad[won]['name']
      seq.append(Func(self.intermessage, wonmsg))
      seq.append(Wait(3.0))
      value=self.pad[won]['set']
    else:
      score=self.humanvscpuscore()
      msg=[
        "Rallies %d x %d = %d"%(
          self.pad[self._HUMANPAD]['totrly'], self._SCOREPOINTS['rallyunit'],
          score['rallies']
        ),
        "Bonus foes = %d"%score['bonus'],
        "Penalty = %d"%score['penalty'],
        "TOTAL SCORE = %d"%sum(score.values())
      ]

      for i in range(1,len(msg)+1):
        seq.append(Func(self.intermessage, "\n".join(msg[:i])))
        seq.append(Func(self.playeffect, 'ball_in'))
        seq.append(Wait(1.5))

      value=sum(score.values())

    if callable(self.gameovercallback):
      fu=Func(self.gameovercallback,
        {
          'opponent': self._SETTINGS['opponent'],
          'winner': self.pad[won]['name'],
          'value': str(value)
        }
      )
    else: fu=Wait(1)

    seq.append(Wait(3.0))
    seq.append(Func(self.intermessage, 'GAME OVER', 0.3))
    seq.append(Wait(1.0))
    seq.append(fu)

    seq.start()

  #-----------------------------------------------------
  #
  def humanvscpuscore(self):
    sco={}
    sco['rallies']=self.pad[self._HUMANPAD]['totrly'] * self._SCOREPOINTS['rallyunit']
    self.dbgprint("@@RLYsco:%r"%sco['rallies'])

    sco['bonus']=self.foesdefeated * self._SCOREPOINTS['bonusunit']
    self.dbgprint("@@BONUS:%r"%sco['bonus'])

    # penalty points will be assigned reaching the set limit to win
    minsets=((self._SETTINGS['sets']/2)+1)*(self.foesdefeated+1)
    sco['penalty']=-(
      self.totsets - minsets
    ) * self._SCOREPOINTS['penaltyunit']
    self.dbgprint("@@PENALTY:sets(%r) ~ foes(%r) ~ minsets(%r)=%r"%(
        self.totsets, self.foesdefeated+1, minsets, sco['penalty']
      )
    )

    self.dbgprint("@@TOTAL SCORE:%r"%sum(sco.values()))
    return sco
  #-----------------------------------------------------
  #
  def playerscore(self, player):
    #
    self.playeffect('ball_out')
    self.setmaintask(0)
    self.ball.setActive(False)
    self.wallbouncheck(reset=True)
    self.pad[player]['gam']+=1
    self.playerturn=player
    self.updatescore()
    # a set is won reaching the games limit self._SETTINGS['games'] but also exceeding the other score by 2 points, e.g.: 6-0 won but 6-5 keep going
    if (
      (
        self.pad[0]['gam'] >= self._SETTINGS['games']
        or self.pad[1]['gam'] >= self._SETTINGS['games']
      ) and abs(self.pad[0]['gam'] - self.pad[1]['gam']) >= 2
    ): self.endset()
    else:
      self.checkmatchball()
      self.ballreset()

  #-----------------------------------------------------
  #
  def checkmatchball(self):
    # the player with set advantage
    p0=0 if self.pad[0]['set'] >= self.pad[1]['set'] else 1
    # the other player
    p1=not p0
    if (
      self.pad[p0]['set'] >= (self._SETTINGS['sets']/2)
    ) and (
      (self.pad[p0]['set'] - self.pad[p1]['set']) >= 1
    ) and (
      self.pad[p0]['gam'] >= (self._SETTINGS['games']-1)
    ) and (
      (self.pad[p0]['gam'] - self.pad[p1]['gam']) >= 1
    ):
      self.dbgprint("@@ MATCH BALL FOR PLAYER\n%s!"%self.pad[p0]['name'])
      self.intermessage(
        "MATCH BALL FOR PLAYER\n%s!"%self.pad[p0]['name'],
        delay=3
      )

  #-----------------------------------------------------
  #
  _bcc=[0,0]
  def wallbouncheck(self, reset=False):
    """ check for triple bounces in a player's middlefield
    """
    if reset: self._bcc=[0,0]
    else:
      # bi=1 if the ball hit @ pos <=0, 0 otherwise
      bi=self.ball.getPosition()[0] <= 0
      # increm pad side hits and 0 the opposite
      self._bcc[bi]+=1
      self._bcc[not bi]=0
      if sum(self._bcc) > 2: return 1 if self._bcc[0] else 0
    return None

  #-----------------------------------------------------
  #
  def ballinpulse(self, vec):
    self.ball.setVelocity(0,0,0)
    self.ball.addImpulse(vec)

  #-----------------------------------------------------
  #
  def ballreset(self, foo=None):
    """ """
    b=self.pad[1]['mdl'].getTightBounds()
    w,n,h=b[1]-b[0]
    z=.67
    self.PADLIMZ=z-(h/2.)

    self.ballNP.hide()
    self.ball.setActive(False)
    self.ball.setVelocity(Vec3(0,0,0))
    self.ball.resetPosition(Point3(0,0,0))
    self._ballprepare()
    self.ball.setActive(True)
    self.ballNP.show()
    self.setmaintask(1)
    self.playeffect('ball_in')

  #-----------------------------------------------------
  #
  def ballrestart(self, foo=None):
    """ to start the ball off the pad """
    self.ignore('space')
    self._ballpreparego()
    p=self.playerturn
    # serve speed - randomply choosed
    bs=random.uniform(self.BALLSPEED*1.0, self.BALLSPEED*2.0)
    self.ballinpulse(Vec3([-bs, bs][p], 0, self.pad[p]['vel']))
    return None

  #-----------------------------------------------------
  #
  def _ballprepare(self):
    p=self.playerturn
    self.ballNP.wrtReparentTo(self.pad[p]['mdl'])
    self.ballNP.setPos([-.08, .08][p], 0, 0)
    if p == 0 and self._SETTINGS['opponent'] == "cpu":
      taskMgr.doMethodLater(3, self.ballrestart, 'gpl01_npcbrstrt')
    else: self.accept('space', self.ballrestart)

  def _ballpreparego(self):
    x,y,z=self.ballNP.getPos(self.field)
    self.ballNP.wrtReparentTo(self.field)
    self.ballNP.setPos(Point3(0,0,0))
    self.ball.resetPosition(Point3(x,0,z))

  #-----------------------------------------------------
  #
  def setpadvel(self, p, v): self.pad[p]['vel']=v

  #-----------------------------------------------------
  #
  _collshow=0
  def toggle_collisions(self):
    self._collshow=not self._collshow
    try:
      l=self.parent.render.findAllMatches("**/+CollisionNode")
      if self._collshow:
        self.parent.cTrav.showCollisions(self.parent.render)
        for cn in l: cn.show()
      else:
        self.parent.cTrav.hideCollisions()
        for cn in l: cn.hide()
    except: self.dbgprint("[cbsnipBase:toggle_collisions] no traverser")

#=========================================================================
#
if __name__ == "__main__":
  """ Demo to show off how to use this class to run the pong game
  press '1' for Human vs computer, '2' for Human vs human
  press 'p' to pause the game
  """
  loadPrcFileData("", """win-size 800 600
  win-origin 0 0
  model-path $MAIN_DIR/data/models/
  sync-video 0
  #show-frame-rate-meter #t
  """
  )
  class world(ShowBase):
    def __init__(self):
      ShowBase.__init__(self)
      self.game=None
      self.accept('escape', sys.exit)
      self.accept('p', self.pausegame)
      self.accept('1', self.startgame)
      self.accept('2', self.startgame2)

    def pausegame(self):
      if self.game: self.game.pause()

    def stopgame(self):
      if self.game:
        self.game.finish()
        del self.game
        self.game=None

    def gocallback(self, score):
      self.dbgprint(">> the scoreboard:\n'%r'"%score)

    def startgame(self):
      self.stopgame()
      if self.game == None:
        self.game=gameplay(
          self, settings={'opponent': 'cpu'}, callback=self.gocallback
        )

    def startgame2(self):
      self.stopgame()
      if self.game == None:
        self.game=gameplay(
          self, settings={'opponent': 'human'}, callback=self.gocallback
        )

  W=world()
  run()
