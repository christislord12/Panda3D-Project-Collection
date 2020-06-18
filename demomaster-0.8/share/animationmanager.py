# Animation Manager
# CL Cheung Apr 2009
import re, traceback, sys, math
from pandac.PandaModules import Vec3,Vec4,Point3,Point2,Mat4
import posemanager

digit_re = '(\d+)'
float_re = '(\-?(\d+)(\.\d*)?)'
comma_re = '(\s*\,\s*)'
RE_animation = re.compile('Animation(\s+)((\w|\.)*):')
RE_fps = re.compile('fps(\s+)%s' % float_re)
RE_frame = re.compile('Frame(\s+)%s:' % digit_re)
animationmode_re = '(smooth|linear|decelerate|accelerate)?'
RE_pose = re.compile('pose(\s+)((\w|\.)*)(\s+)%s(\s*)%s(\s*)$' % (digit_re,animationmode_re))
RE_defaultmode = re.compile('default(\s+)%s' % animationmode_re)
RE_gravity = re.compile('gravity(\s+)%s' % digit_re)
#float3_re = '\(\s*%s%s%s%s%s\s*\)' % (float_re,comma_re,float_re,comma_re,float_re)
#RE_float3 = re.compile(float3_re)

##def smoothstep(minv, maxv, x):
##    if x < minv: return 0
##    if x >= maxv: return 1
##    f = ((x - minv) / (maxv - minv))
##    return -2 * pow(f, 3) + 3 * pow(f, 2)

def smoothstep(f):
    return -2 * pow(f, 3) + 3 * pow(f, 2)

AM_UNKNOWN = 0
AM_SMOOTH = 1
AM_LINEAR = 2
AM_DECELERATE = 3
AM_ACCELERATE = 4
def animationmode_lookup(mode):
    if mode == "smooth":
        return AM_SMOOTH
    if mode == "linear":
        return AM_LINEAR
    if mode == "decelerate":
        return AM_DECELERATE
    if mode == "accelerate":
        return AM_ACCELERATE
    return AM_UNKNOWN


def fix(constraint,jointname,v):
    if jointname in constraint:
        low,high = constraint[jointname]
        return Vec3(min(max(v[0],low[0]),high[0]),
            min(max(v[1],low[1]),high[1]),
            min(max(v[2],low[2]),high[2]))
    else:
        return v

def fix1(constraint,jointname,v):
    if jointname in constraint:
        low,high = constraint[jointname]
        return min(max(v,low),high)
    else:
        return v

def adjustAngles(v):
    if v[0] > 180:
        v.setX(v[0] - 360)
    elif v[0] < -180:
        v.setX(v[0] + 360)

    if v[1] > 180:
        v.setY(v[1] - 360)
    elif v[1] < -180:
        v.setY(v[1] + 360)

    if v[2] > 180:
        v.setZ(v[2] - 360)
    elif v[2] < -180:
        v.setZ(v[2] + 360)

    return v


def mysetHpr(np, v, vf):
    if v[0] >= 99999 or v[1] >= 99999 or v[2] >= 99999:
        if v[0] < 99999:
            np.setH(vf[0])
        if v[1] < 99999:
            np.setP(vf[1])
        if v[2] < 99999:
            np.setR(vf[2])
    else:
        np.setHpr(vf)

class FrameDef():
    CMD_GRAVITY = 101
    CMD_EVENT = 102
    def __init__(self, framenumber):
        self.framenumber = framenumber
        self.posedictlist = []
        self.jointinfo = []
        self.cmdlist = []

    def setGravity(self, v):
        self.cmdlist.append([self.CMD_GRAVITY, v])

    def setEvent(self, event, info):
        self.cmdlist.append([self.CMD_EVENT, event, info])

    def setPose(self, actor, poserepositoty, posename, length, mode, factor=1.0):
        jointdict = {}
        ok, othercmds = poserepositoty.getPose(actor, posename, jointdict)
        if ok:
            if len(jointdict) > 0:
                self.posedictlist.append((jointdict,length,mode,factor))
            self.cmdlist += othercmds
            return True
        return False

    def finalize(self):
        # compute how much value a pose is contribute for a common joint, if any
        # get all the joint list
        jointlist = []
        for entry in self.posedictlist:
            jointdict,length,mode,factor = entry
            for joint in jointdict:
                if joint not in jointlist:
                    jointlist.append(joint)

        mlength = 0
        for joint in jointlist:
            jointcount = 0
            valuelist = [[], [], []]
            #pos = Vec3(0,0,0)
            for entry in self.posedictlist:
                jointdict,length,mode,factor = entry
                mlength = max(mlength,length)
                if joint in jointdict:
                    jointcount += 1
                    l = jointdict[joint]
                    for pair in l:
                        cmd,value = pair
                        valuelist[cmd].append((value,length,mode,factor))
            for i in range(3):
                if len(valuelist[i]) > 0:
                    if i == 2:
                        pos = 0.0
                    else:
                        pos = Vec3(0,0,0)
                    for pair in valuelist[i]:
                        value,length,mode,factor = pair
                        mlength = max(mlength,length)
                        pos += value / jointcount * factor
                    self.jointinfo.append((joint,i,pos,length,mode))
        self.maxlen = mlength
        #print "maxlne", self.maxlen
        self.posedictlist = []

    def Dump(self):
        print "-------"
        print "Frame ", self.framenumber
        for info in self.jointinfo:
            joint,cmd,pos,length,mode = info
            print joint,cmd,pos,length,mode

    def updateJoint(self, actor, framenumber, posDict, hprDict, morphDict, posConstraint, hprConstraint, morphConstraint):
        for info in self.jointinfo:
            jointname,cmd,v,length,mode = info
            if cmd == posemanager.PoseRepository.CMD_POS:
                np = actor.pjoints[jointname].np
            elif cmd == posemanager.PoseRepository.CMD_HPR:
                np = actor.joints[jointname].np
            elif cmd == posemanager.PoseRepository.CMD_MORPH:
                np = actor.morphs[jointname].np
            #print "Length", length, self.framenumber, framenumber
            if length == 0 or self.framenumber + length < framenumber:
                if cmd == posemanager.PoseRepository.CMD_HPR:
                    if hprDict[jointname][1] >= self.framenumber + length:
                        continue
                    vf = fix(hprConstraint,jointname,v)
                    mysetHpr(np, v, vf)
                    #np.setHpr(vf)
                    hprDict[jointname] = [vf,self.framenumber + length]
                elif cmd == posemanager.PoseRepository.CMD_POS:
                    if posDict[jointname][1] >= self.framenumber + length:
                        continue
                    vf = fix(posConstraint,jointname,v)
                    np.setPos(vf)
                    posDict[jointname] = [vf,self.framenumber + length]
                elif cmd == posemanager.PoseRepository.CMD_MORPH:
                    if morphDict[jointname][1] >= self.framenumber + length:
                        continue
                    vf = fix1(morphConstraint,jointname,v)
                    np.setX(vf)
                    morphDict[jointname] = [vf,self.framenumber + length]
            else:
                ratio = float(framenumber - self.framenumber) / length
                if mode == AM_SMOOTH:
                    ratio = smoothstep(ratio)
                elif mode == AM_DECELERATE:
                    ratio = 1 - (1-ratio) * (1-ratio)
                elif mode == AM_ACCELERATE:
                    ratio = ratio * ratio
                #print "Ratio", ratio
                if cmd == posemanager.PoseRepository.CMD_HPR:
                    hpr = hprDict[jointname][0]
                    vf = (v - hpr) * ratio + hpr
                    vf = fix(hprConstraint,jointname,vf)
                    mysetHpr(np, v, vf)
                    #np.setHpr(vf)
                elif cmd == posemanager.PoseRepository.CMD_POS:
                    pos = posDict[jointname][0]
                    vf = (v - pos) * ratio + pos
                    vf = fix(posConstraint,jointname,vf)
                    np.setPos(vf)
                elif cmd == posemanager.PoseRepository.CMD_MORPH:
                    pos = morphDict[jointname][0]
                    vf = (v - pos) * ratio + pos
                    vf = fix1(morphConstraint,jointname,vf)
                    np.setX(vf)


class AnimationDef():
    def __init__(self, name):
        self.name = name
        self.frameList = []
        self.fps = 1
        self.defaultmode = AM_SMOOTH

    def Dump(self):
        print "Animation ", self.name
        print "fps ", self.fps
        print "total: %d frame defined, from frame %d to frame %d" % (len(self.frameList), self.frameList[0].framenumber, self.frameList[-1].framenumber)
        for frame in self.frameList:
            frame.Dump()

    def finalize(self):
        #start = self.frameList[0].framenumber
        #end = self.frameList[-1].framenumber
        # compute the list of joints used in this animation\
        self.allJoints = set()
        self.allPJoints = set()
        self.allMorphs = set()
        for frame in self.frameList:
            for info in frame.jointinfo:
                joint,cmd,pos,length,mode = info
                if cmd == posemanager.PoseRepository.CMD_HPR:
                    self.allJoints.add(joint)
                elif cmd == posemanager.PoseRepository.CMD_POS:
                    self.allPJoints.add(joint)
                elif cmd == posemanager.PoseRepository.CMD_MORPH:
                    self.allMorphs.add(joint)


class AnimationRepository():
    def __init__(self, pr):
        self.animationList = {}
        self.pr = pr

    def Dump(self):
        for animation in self.animationList:
            print "=============================="
            self.animationList[animation].Dump()

    def ReadFile(self, actor, filename):
        try:
            f = open(filename, "r")
            if f != None:
                lines = f.read()
                fOk, result = self.Parse(lines, actor)
                f.close()
                self.filename = filename
                return fOk, result
        except Exception,e:
            traceback.print_exc(file=sys.stdout)
        return False, "Unable to open file: %s" % filename

    def Reload(self, actor):
        self.animationList = {}
        return self.ReadFile(actor, self.filename)

    def Parse(self, buffer, actor):
        lines  = buffer.split("\n")
        animation = None
        frame = None
        linenumber = 0
        for oline in lines:
            line = oline.strip()
            linenumber += 1
            if len(line) == 0 or line[0] == "#":
                # comment
                continue
            r = re.search(RE_animation, line)
            if r != None:
                # a new animation definition
                if animation != None:
                    if frame != None:
                        frame.finalize()
                        #if len(frame.jointinfo) == 0:
                            #return False, "No frame defined for animation %s, frame %d" % (animation.name,frame.framenumber)
                        animation.frameList.append(frame)
                    frame = None
                    if len(animation.frameList) == 0:
                        return False, "Empty animation definition for %s" % animation.name
                    else:
                        animation.finalize()
                        self.animationList[animation.name] = animation
                animationname = r.group(2)
                if animationname in self.animationList:
                    return False, "Duplicate animation definition for %s" % animationname
                animation = AnimationDef(animationname)
                continue

            if animation == None:
                return False, "Animation not defined"

            r = re.search(RE_fps, line)
            if r != None:
                animation.fps = float(r.group(2))
                continue

            r = re.search(RE_defaultmode, line)
            if r != None:
                animation.defaultmode = animationmode_lookup(r.group(2))
                continue

            r = re.search(RE_frame, line)
            if r != None:
                if frame != None:
                    frame.finalize()
                    #if len(frame.jointinfo) == 0:
                        #return False, "No frame defined for animation %s, frame %d" % (animation.name,frame.framenumber)
                    animation.frameList.append(frame)
                    frame = None
                framenumber = int(r.group(2))
                #print "adding frame", framenumber
                frame = FrameDef(framenumber)
                continue
            if frame == None:
                return False, "Line at %d, Frame not defined" % linenumber

            r = re.search(RE_pose, line)
            if r != None:
                posename = r.group(2)
                length = int(r.group(5))
                if r.group(7) == None:
                    mode = animation.defaultmode
                else:
                    mode = animationmode_lookup(r.group(7))
                #print "length is",length
                if not frame.setPose(actor, self.pr, posename, length, mode):
                    return False, "Line at %d, Invalid pose %s" % (linenumber, posename)
                continue
            r = re.search(RE_gravity, line)
            if r != None:
                v  = int(r.group(2))
                frame.setGravity(v)
                continue

            return False, "Line at %d, Unknown definition '%s'" % (linenumber, line)

        if animation != None:
           if frame != None:
                frame.finalize()
                #if len(frame.jointinfo) == 0:
                    #return False, "No frame defined for animation %s, frame %d" % (animation.name,frame.framenumber)
                animation.frameList.append(frame)
           if len(animation.frameList) == 0:
                 return False, "Empty animation definition for %s" % animation.name
           else:
                 animation.finalize()
                 self.animationList[animation.name] = animation

        return True, ''

    def createAnimation(self, actor, animationname, fps = None):
        if animationname not in self.animationList:
            return None

        return Animation(actor, self.animationList[animationname], fps)

class Animation():
    def __init__(self, actor, animationdef, fps=None, name=None):
        self.actor = actor
        self.animationdef = animationdef
        if fps == None:
            fps = animationdef.fps
        self.setFps(fps)
        self.fcontinue = False
        self.pendingStart = False
        if name == None:
            self.name = self.animationdef.name
        else:
            self.name = name

        self.posConstraint = actor.posConstraint
        self.hprConstraint = actor.hprConstraint
        self.morphConstraint = actor.morphConstraint
        self.setGround(0)

    def setGround(self, Z):
        self.groundLevel = Z

    def setFps(self, fps):
        self.fps = fps
        self.firstframe = 1
        end = self.animationdef.frameList[-1].framenumber
        self.totalframes = end-self.firstframe
        self.totaltime = float(self.totalframes) / fps

    def start(self, framenumber=1, loop=False):
        self.loop = loop
        self.fcontinue = True
        self.dt = 0
        self.speed = 1
        # record the position and hpr for all joints
        self.posDict = {}
        self.hprDict = {}
        self.morphDict = {}
        for joint in self.animationdef.allJoints:
            hpr = self.actor.joints[joint].np.getHpr()
            self.hprDict[joint] = [hpr,-1]
        for joint in self.animationdef.allPJoints:
            pos = self.actor.pjoints[joint].np.getPos()
            self.posDict[joint] = [pos,-1]
        for joint in self.animationdef.allMorphs:
            pos = self.actor.morphs[joint].np.getX()
            self.morphDict[joint] = [pos,-1]

        if loop:
            self.posDictSave = self.posDict.copy()
            self.hprDictSave = self.hprDict.copy()


        self.currentframe = 0
        self.nextframeindex = 0
        self.gravity = False
        self.activeFrames = []
        self.advanceFrame(framenumber)


    def advanceFrame(self, framenumber):
        #print framenumber
        activeFrames = []
        for frame in self.activeFrames:
            #print frame.framenumber
            #print frame.maxlen
            if frame.framenumber + frame.maxlen >= framenumber:
                activeFrames.append(frame)
            frame.updateJoint(self.actor, framenumber, self.posDict, self.hprDict, self.morphDict, self.posConstraint, self.hprConstraint, self.morphConstraint)

        while self.nextframeindex < len(self.animationdef.frameList):
            frame = self.animationdef.frameList[self.nextframeindex]
            #print frame.framenumber
            #print frame.maxlen
            #print frame.framenumber + frame.maxlen
            if frame.framenumber > framenumber:
                break
            if frame.framenumber + frame.maxlen > framenumber:
                activeFrames.append(frame)
            else:
                frame.updateJoint(self.actor, framenumber, self.posDict, self.hprDict, self.morphDict, self.posConstraint, self.hprConstraint, self.morphConstraint)
            for cmd in frame.cmdlist:
                if cmd[0] == FrameDef.CMD_GRAVITY:
                   self.gravity = cmd[1] > 0
                elif cmd[0] == posemanager.PoseRepository.CMD_SETCONSTRAINTOFF:
                    if cmd[2] == "hpr":
                        dict = self.hprConstraint
                    else:
                        dict = self.posConstraint
                    if cmd[1] in dict:
                        del dict[cmd[1]]
                elif cmd[0] == posemanager.PoseRepository.CMD_SETCONSTRAINT:
                    if cmd[2] == "hpr":
                        dict = self.hprConstraint
                    else:
                        dict = self.posConstraint
                    dict[cmd[1]] = (cmd[3], cmd[4])
            self.nextframeindex += 1
        self.activeFrames = activeFrames
        self.currentframe = framenumber

        if self.gravity:
            np = self.actor.joints["me"].np
            bounds=np.getTightBounds()
            box=bounds[1]-bounds[0]
            #print bounds[0]
            Z = bounds[0][2]
            delta = self.groundLevel - Z
            v = np.getZ()
            np.setZ(v+delta)

    def isRunning(self):
        return self.fcontinue

    def stop(self):
        self.fcontinue = False

    def resume(self):
        self.fcontinue = True

    def setLoop(self, loop):
        self.loop = loop

    def setSpeed(self, speed):
        self.speed = speed

    def update(self, dt):
        if not self.fcontinue:
            return
        dt *= self.speed
        self.dt += dt
        if self.loop:
            if self.dt > self.totaltime:
                self.nextframeindex = 0
                self.posDict = self.posDictSave.copy()
                self.hprDict = self.hprDictSave.copy()
                self.activeFrames = []
            self.dt = delta = math.fmod(self.dt,self.totaltime)
            #print delta
        else:
            delta = self.dt
            if delta > self.totaltime:
                self.fcontinue = False
                self.dt = delta = self.totaltime

        newframenumber = (delta/self.totaltime*self.totalframes) + self.firstframe
        self.advanceFrame(newframenumber)


class AnimationManager():
    def __init__(self):
        self.animations = set()
        taskMgr.add(self.run, "myAnimationManager")
        self.pendings = {}

    def Destroy(self):
        self.animations.clear()
        self.pendings.clear()
        taskMgr.remove("myAnimationManager")

    def remove(self, animation):
        if animation in self.animations:
            self.animations.remove(animation)
            if animation in self.pendings:
                del self.pendings[animation]


    def add(self, animation):
        self.animations.add(animation)

    def append(self, animation, nextanimation, loop):
        self.pendings[animation] = (nextanimation, loop)

    def getAnimation(self, animationname):
        for animation in self.animations:
            if animation.name == animationname:
                return animation
        return None

    def run(self, task):
        #print task.time, globalClock.getRealTime()
        dt = globalClock.getDt()
        for animation in self.animations:
            if animation.isRunning():
                animation.update(dt)
                if not animation.isRunning():
                    if animation in self.pendings:
                        next,loop = self.pendings[animation]
                        del self.pendings[animation]
                        next.start(loop=loop)
        return task.cont

    def clearAll(self):
        self.animations.clear()

if __name__ == '__main__':
    pr = posemanager.PoseRepository(None)
    ok, err = pr.ReadFile("d:\\develop\\panda3d\\test3\\demo_human\\models\\david1\\pose\\basic1.pose")
    if not ok:
        print err
        exit()
    ar = AnimationRepository(pr)
    print ar.ReadFile("d:\\develop\\panda3d\\test3\\demo_human\\models\\david1\\pose\\animation1.ani")
    ar.Dump()
    #animation = ar.createAnimation("CloseFingerOneByOne")
    #animation.start(1, False, 0)
    #animation.update(0)
    #animation.update(1)
    #animation.update(2)
    #animation.update(3)


##
##Animation CloseFingerOneByOne:
##	fps 100
##	Frame 1:
##		pose F2.Close.L
##		pose F2.Close.R
##	Frame 100:
##		pose F3.Close.L
##		pose F3.Close.R
##	Frame 200:
##		pose F3.Open.L
##		pose F3.Open.R
