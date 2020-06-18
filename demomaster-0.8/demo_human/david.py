from direct.actor.Actor import Actor
from pandac.PandaModules import TransparencyAttrib
import hair, geomutil

class myJoint():
    def __init__(self, np):
        self.np = np
        self.defaultPos = np.getPos()
        self.defaultHpr = np.getHpr()

class David():
    def __init__(self):
        self.morphlist = []
        self.jointlist = [
                    "me",
                    "Hip","Back01","Back02","Back03","Back04",
                    "Neck", "Jaw","Breast",
                    "Eye.L","Eye.R",
                    "UpperLid.L","UpperLid.R",
                    "LowerLid.L","LowerLid.R",
                    "Eyebrows.L","Eyebrows.R",

                    # arm
                        "Shoulder.L","Shoulder.R",
                        "Forearm.L","Forearm.R",
                        "Bicep.L","Bicep.R",
                        "Wrist.L","Wrist.R",
                        "Pinky3.L","Pinky3.R",
                        "Pinky2.L","Pinky2.R",
                        "Pinky1.L","Pinky1.R",
                        "Ring3.L","Ring3.R",
                        "Ring2.L","Ring2.R",
                        "Ring1.L","Ring1.R",
                        "Middle3.L","Middle3.R",
                        "Middle2.L","Middle2.R",
                        "Middle1.L","Middle1.R",
                        "Index3.L","Index3.R",
                        "Index2.L","Index2.R",
                        "Index1.L","Index1.R",
                        "Thumb3.L","Thumb3.R",
                        "Thumb2.L","Thumb2.R",
                        "Thumb1.L","Thumb1.R",
                    # Leg
                        "Thing.L","Thing.R",
                        "Calf.L","Calf.R",
                        "Ankle.L","Ankle.R",
                    "Mouth.U","Mouth.D",

                    ]
        self.pjointlist = [
                    "me",
                    "Mouth.L","Mouth.R",
                    "Mouth.U","Mouth.D",
                    "EyeMiddle",
                    "Eyebrows.L","Eyebrows.R",
            ]
        self.joints = {}
        self.pjoints = {}
        self.posConstraint = {}
        self.hprConstraint = {}
        self.morphConstraint = {}

        self.hairs = None

    def Load(self):
        self.model = Actor("models/david1/david1.egg")
        #self.model = Actor("models/david1/david1.egg", {'walk' : 'models/david1/david1-anim1.egg'})
        #self.model = loader.loadModel("models/david1/david1.egg")
        if self.model:
            #self.model.setTransparency(TransparencyAttrib.MDual)
            for joint in self.jointlist:
                if joint == "me":
                    self.joints["me"] = myJoint(self.model)
                else:
                    j = self.model.controlJoint(None, 'modelRoot', joint)
                    #j = self.model.exposeJoint(None, 'modelRoot', joint)
                    if j != None:
                        self.joints[joint] = myJoint(j)


            for joint in self.pjointlist:
                if joint in self.jointlist:
                    self.pjoints[joint] = self.joints[joint]
                else:
                    if joint == "me":
                        self.pjoints["me"] = myJoint(self.model)
                    else:
                        j = self.model.controlJoint(None, 'modelRoot', joint)
                        #j = self.model.exposeJoint(None, 'modelRoot', joint)
                        if j != None:
                            self.pjoints[joint] = myJoint(j)

            self.hairnp = self.model.find("**/Hair")
            self.headjoint = self.model.exposeJoint(None, 'modelRoot', 'HeadDeform')
            self.setupHair(False)
            return True
        else:
            return False
            #self.model.listJoints()
#            self.joints["Eye.L"].lookAt(2.5,10,1)
#            self.joints["Eye.R"].lookAt(2.5,10,1)



    def setupHair(self, showHair):
        if showHair:
            if self.hairs == None:
                vertexinfo = geomutil.getVertexInfo(self.hairnp, self.headjoint)
                self.hairs = hair.Hairs(self.headjoint)
                self.hairs.BuildHairs(vertexinfo)
                self.hairnp.show()
        else:
            if self.hairs != None:
                self.hairs.Destroy()
                self.hairs = None
            self.hairnp.hide()
