# Pose Manager
# CL Cheung Apr 2009
import re, traceback, sys
from pandac.PandaModules import Vec3,Vec4,Point3,Point2,Mat4

float_re = '(\-?(\d*)(\.\d*)?)'
comma_re = '(\s*\,\s*)'
RE_pose = re.compile('^Pose(\s+)((\w|\.)*)(\s*):(\s*)$')
RE_hprposmorph = re.compile('^(hpr|pos|morph)(\s+)((\w|\.)*)(\s*)(.*)')
RE_getpose = re.compile('^getpose(\s+)((\w|\.)*)(\s*)$')
float3_re = '\(\s*%s%s%s%s%s\s*\)' % (float_re,comma_re,float_re,comma_re,float_re)
RE_float = re.compile(float_re)
RE_float3 = re.compile(float3_re)

RE_setconstraintoff = re.compile('^constraint(\s+)((\w|\.)*)(\s+)(hpr|pos)(\s+)off(\s*)$')
RE_setconstraint = re.compile('^constraint(\s+)((\w|\.)*)(\s+)(hpr|pos)(\s+)%s(\s+)%s(\s*)$' % (float3_re,float3_re))

def mirror_joint(jointname):
    if jointname[-2:] == ".L":
        return jointname[:-1] + "R"
    if jointname[-2:] == ".R":
        return jointname[:-1] + "L"
    return ""

class PoseRepository():
    CMD_HPR = 0
    CMD_POS = 1
    CMD_MORPH = 2
    CMD_GETPOSE = 3
    CMD_SETCONSTRAINTOFF = 4
    CMD_SETCONSTRAINT = 5
    def __init__(self):
        self.poseList = {}

    def GetPoseList(self):
        ret = []
        for pose in self.poseList:
            ret.append(pose)
        return ret

    def _ReadFile(self, actor, filename):
        try:
            f = open(filename, "r")
            if f != None:
                lines = f.read()
                fOk, result = self.Parse(lines, actor)
                f.close()
                #self.filename = filename
                return fOk, result
        except Exception,e:
            traceback.print_exc(file=sys.stdout)
        return False, "Unable to open file: %s" % filename

    def LoadFiles(self, actor, dir, filelist):
        self.Reset()
        for file in filelist:
            ok, err = self._ReadFile(actor, dir + file)
            if not ok:
                return False, (file, err)
        self.loadinfo = (dir, filelist)
        return True, None

    def Reset(self):
        self.poseList = {}

    def Reload(self, actor):
        self.poseList = {}
        return self.LoadFiles(actor, self.fileinfo[0], self.fileinfo[1])

    def Parse(self, buffer, actor):
        ok, result = self.ParseSide(buffer, False, actor)
        if ok:
            ok, result = self.ParseSide(buffer, True, actor)
        return ok,result

    def ParseSide(self, buffer, mirror, actor):
        lines  = buffer.split("\n")
        cmds = []
        posename = None
        linenumber = 0
        skippose = False
        for oline in lines:
            line = oline.strip()
            linenumber += 1
            if len(line) == 0 or line[0] == "#":
                # comment
                continue
            r = re.search(RE_pose, line)
            if r != None:
                # a new pose definition
                if posename != None:
                    if len(cmds) == 0:
                        return False, "Empty pose definition for %s" % posename
                    else:
                        self.poseList[posename] = cmds
                        cmds = []
                posename = r.group(2)
                skippose = False
                if mirror:
                    posename = mirror_joint(posename)
                    if len(posename) == 0 or posename in self.poseList:
                        skippose = True
                        posename = None

                if posename != None and posename in self.poseList:
                    return False, "Duplicate pose definition for %s" % posename
                continue
            if skippose:
                continue
            r = re.search(RE_hprposmorph, line)
            if r != None:
                hprposmorph = r.group(1)
                if hprposmorph == "hpr":
                    icmd = self.CMD_HPR
                elif hprposmorph == "pos":
                    icmd = self.CMD_POS
                else:
                    icmd = self.CMD_MORPH
                jointname = r.group(3)
                #print hprpos,jointname," ",r.group(2)," ",r.group(4)
                thismirror = False
                if mirror:
                    jointname = mirror_joint(jointname)
                    if len(jointname) == 0:
                        jointname = r.group(3)
                    else:
                        thismirror = True
                if actor and \
                    (jointname not in actor.joints and icmd == self.CMD_HPR) and \
                    (jointname not in actor.pjoints and icmd == self.CMD_POS) and \
                    (jointname not in actor.morphs and icmd == self.CMD_MORPH):
                    return False, "Joint: %s not defined in Actor" % jointname
                command = r.group(6).strip()
                if command == "Default":
                    if icmd == self.CMD_MORPH:
                        cmds.append([icmd,jointname,0.0])
                    else:
                        cmds.append([icmd,jointname,None])
                    continue

                if icmd == self.CMD_MORPH:
                    r = re.search(RE_float, command)
                    f1 = float(r.group(1))
                    cmds.append([icmd,jointname,f1])
                    continue
                else:
                    r = re.search(RE_float3, command)
                    if r != None:
                        f1 = float(r.group(1))
                        f2 = float(r.group(5))
                        f3 = float(r.group(9))
                        if thismirror:
                            f1 = -f1
                            f3 = -f3
                        cmds.append([icmd,jointname,[f1,f2,f3]])
                        continue
                return False, "Error at line %d: Invalid hpr values: %s" % (linenumber, line)
            r = re.search(RE_getpose, line)
            if r != None:
                getposename = r.group(2).strip()
                if mirror:
                    getposename = mirror_joint(getposename)
                    if len(getposename) == 0:
                        getposename = r.group(2).strip()

                if len(getposename) == 0 or getposename not in self.poseList:
                    return False, "Invalid pose name at Line %d: %s" % (linenumber, line)
                cmds.append([self.CMD_GETPOSE,getposename])
                continue
            r = re.search(RE_setconstraintoff, line)
            if r != None:
                jointname = r.group(2).strip()
                hprpos = r.group(5)
                if actor and jointname not in actor.joints and hprpos == "hpr":
                    return False, "Joint: %s not defined in Actor" % jointname
                if actor and jointname not in actor.pjoints and hprpos == "pos":
                    return False, "Joint: %s not defined in Actor" % jointname

                cmds.append([self.CMD_SETCONSTRAINTOFF,jointname,hprpos])
                continue
            r = re.search(RE_setconstraint, line)
            if r != None:
                jointname = r.group(2).strip()
                hprpos = r.group(5)
                if actor and jointname not in actor.joints and hprpos == "hpr":
                    return False, "Joint: %s not defined in Actor" % jointname
                if actor and jointname not in actor.pjoints and hprpos == "pos":
                    return False, "Joint: %s not defined in Actor" % jointname
                #print jointname,hprpos
                cmds.append([self.CMD_SETCONSTRAINT,jointname,hprpos,
                    Vec3(float(r.group(7)),float(r.group(11)),float(r.group(15))),
                    Vec3(float(r.group(19)),float(r.group(23)),float(r.group(27)))])
                continue

            return False, "Error at line %d: %s" % (linenumber, line)
        if posename != None:
            if len(cmds) == 0:
                return False, "Empty post definition for %s" % posename
            else:
                self.poseList[posename] = cmds

        return True, ""

    def setPose(self, actor, posename):
        if posename in self.poseList:
            posecmds = self.poseList[posename]
            for cmd in posecmds:
                if cmd[0] == self.CMD_HPR:
                    joint = actor.joints[cmd[1]]
                    if cmd[2] == None:
                        hpr = joint.defaultHpr
                    else:
                        hpr = Vec3(*cmd[2])
                    joint.np.setHpr(hpr)
                elif cmd[0] == self.CMD_POS:
                    joint = actor.pjoints[cmd[1]]
                    if cmd[2] == None:
                        pos = joint.defaultPos
                    else:
                        pos = Vec3(*cmd[2])
                    joint.np.setPos(pos)
                elif cmd[0] == self.CMD_MORPH:
                    joint = actor.morphs[cmd[1]]
                    if cmd[2] == None:
                        pos = joint.defaultPos
                    else:
                        pos = cmd[2]
                    joint.np.setX(pos)
                elif cmd[0] == self.CMD_GETPOSE:
                    self.setPose(actor, cmd[1])
            return True
        return False


    def getPose(self, actor, posename, jointdict):
        if posename in self.poseList:
            posecmds = self.poseList[posename]
            othercommands = []
            for cmd in posecmds:
                if cmd[0] == self.CMD_HPR:
                    if cmd[2] == None:
                        joint = actor.joints[cmd[1]]
                        hpr = joint.defaultHpr
                    else:
                        hpr = Vec3(*cmd[2])
                    if cmd[1] in jointdict:
                        jointdict[cmd[1]].append((cmd[0], hpr))
                    else:
                        jointdict[cmd[1]] = [(cmd[0], hpr)]
                elif cmd[0] == self.CMD_POS:
                    if cmd[2] == None:
                        joint = actor.pjoints[cmd[1]]
                        pos = joint.defaultPos
                    else:
                        pos = Vec3(*cmd[2])
                    if cmd[1] in jointdict:
                        jointdict[cmd[1]].append((cmd[0], pos))
                    else:
                        jointdict[cmd[1]] = [(cmd[0], pos)]
                elif cmd[0] == self.CMD_MORPH:
                    pos = cmd[2]
                    if cmd[1] in jointdict:
                        jointdict[cmd[1]].append((cmd[0], pos))
                    else:
                        jointdict[cmd[1]] = [(cmd[0], pos)]
                elif cmd[0] == self.CMD_GETPOSE:
                    self.getPose(actor, cmd[1], jointdict)
                else:
                    othercommands.append(cmd)
            return True, othercommands
        return False, None

if __name__ == '__main__':
    #import david
    #d = david.David()
    pr = PoseRepository(None)

    if False:
        #e = re.compile(float_re)
        #r = re.search(e, "1.5")
        #print r.group(0)

        r = re.search(RE_hpr, "hpr Index3.L Default")
        print r.group(2) # Index3.L
        print r.group(5) # Default
        r = re.search(RE_hpr, "hpr Index3.L (1,2,3)")
        print r.group(2) # Index3.L
        print r.group(5) # Default

    if False:
        #print float3_re
        r = re.search(RE_float3, "(-10.,2.5,-3.02)")
        print r.group(1)
        print r.group(5)
        print r.group(9)

        e = re.compile("\(%s%s%s\)" % (float_re,comma_re,float_re))
        r = re.search(e, "(1.5,1)")
        print r.group(0)

    #exit()
    ok, err = pr.ReadFile("d:\\develop\\panda3d\\test3\\demo_human\\models\\david1\\pose\\basic1.pose")
    if not ok:
        print err
    else:
        print pr.poseList
##Pose F1.Open.L:
##	hpr Index3.L (-40.9,2.4,-11.82)
##	hpr Index2.L Default
##	hpr Index1.L Default
### close index finger
##Pose F1.Close.L:
##	hpr Index3.L (-65.9,-20,-25.12)
##	hpr Index2.L: (-108.84,-48.86,-125.58)
##	hpr Index1.L (0,-92,0)


