import sys, random, time
from math import degrees, sin, cos, pi, sqrt, pow, atan
from direct.showbase import PythonUtil as PU
#import ode as ode
#import direct.directbase.DirectStart
from pandac.PandaModules import PerspectiveLens
from pandac.PandaModules import TransparencyAttrib,GeomVertexReader,GeomVertexFormat,GeomVertexData,Geom,GeomVertexWriter,GeomTriangles,GeomNode
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup, OdeSpace, OdeBallJoint, OdeHinge2Joint, OdeQuadTreeSpace, OdeHashSpace
from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdeBoxGeom, OdePlaneGeom, OdeCylinderGeom, OdeCappedCylinderGeom, OdeTriMeshGeom, OdeTriMeshData
from pandac.PandaModules import BitMask32, Quat, Mat4
from pandac.PandaModules import PandaSystem

#from random import randint, random
import random

def getLength(v1,v2):
    return sqrt(pow(v1[0]-v2[0],2)+pow(v1[1]-v2[1],2)+pow(v1[2]-v2[2],2))
def getCenter(v1,v2):
    return [ (v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2]

class ODEBallJoint(OdeBallJoint):
    def __init__(self, world, model=None, renderparent=None, scale=None):
        OdeBallJoint.__init__(self, world)
        if model != None:
            self.np = model.copyTo(renderparent)
            self.np.setP(90)
            self.np.flattenStrong()
            self.scale = scale
        else:
            self.np = None
        self.bodies = 0

    def destroy(self):
        self.detach()
        OdeBallJoint.destroy(self)
        if self.np != None:
            self.np.removeNode()

    def attach(self, b1, b2):
        OdeBallJoint.attach(self, b1,b2)
        self.body1 = b1
        if b2 == None:
            self.bodies = 1
        else:
            self.bodies = 2
            self.body2 = b2

    def Render(self):
        if self.np==None or self.bodies == 0:
            return
        #v = self.getAnchor()
        if self.bodies == 1:
            v = self.getAnchor2()
        else:
            #v = self.getBody(1).getPosition()
            v = self.body2.getPosition()
        #vb = self.getBody(0).getPosition()
        vb = self.body1.getPosition()
        #if self.bodies == 2:
        #    print v, vb
        v = Vec3(v[0],v[1],v[2])
        vb = Vec3(vb[0],vb[1],vb[2])
        c = (vb+v) / 2
        vd = vb-v
        l = vd.length()
        #self.np.setScale(self.scale[0], self.scale[1], self.scale[2] * l)
        self.np.setScale(self.scale[0], self.scale[1] *l, self.scale[0])
        self.np.setPos(c[0],c[1],c[2])
        self.np.lookAt(vb[0],vb[1],vb[2])


##class ODEBallJointOld(OdeBallJoint):
##    def __init__(self, world, model=None, renderparent=None, scale=None):
##        OdeBallJoint.__init__(self, world)
##        if model != None:
##            self.np = renderparent.attachNewNode("dummy")
##            np = model.copyTo(self.np)
##            np.setP(90)
##            self.np2 = np
##
##            self.scale = scale
##        else:
##            self.np = None
##
##    def destroy(self):
##        self.detach()
##        OdeBallJoint.destroy(self)
##        if self.np != None:
##            self.np.removeNode()
##
##    def Render(self):
##        if self.np==None:
##            return
##        #v = self.getAnchor()
##        v = self.getAnchor2()
##        vb = self.getBody(0).getPosition()
##        v = Vec3(v[0],v[1],v[2])
##        vb = Vec3(vb[0],vb[1],vb[2])
##        c = (vb+v) / 2
##        vd = vb-v
##        l = vd.length()
##        #self.np.setScale(self.scale[0], self.scale[1], self.scale[2] * l)
##        #self.np.setScale(self.scale[0], self.scale[1] *l, self.scale[2])
##        self.np2.setScale(self.scale[0], self.scale[1], self.scale[2] * l)
##        self.np.setPos(c[0],c[1],c[2])
##        self.np.lookAt(vb[0],vb[1],vb[2])


class ODEobjbase:
    def storeProps(self, realObj, mass, surfaceId, collideBits, categoryBits):
        self.realObj=realObj
        self.mass=mass
        self.surfaceId = surfaceId
        self.geom.getSpace().setSurfaceType(self.geom, surfaceId)
        self.geom.setCollideBits(BitMask32(collideBits))
        self.geom.setCategoryBits(BitMask32(categoryBits))

    def isDynamic(self):
        return hasattr(self,'body')

    def delRealobj(self):
        if self.realObj != None:
            self.realObj.removeNode()
            self.realObj = None

    def destroy(self):
        if hasattr(self,'body'):
            #self.body.destroy()
            del self.body
        self.geom.getSpace().remove(self.geom)

        del self.geom
        if hasattr(self,'visualizer'):
           self.visualizer.removeNode()
        self.delRealobj()


    def getOBB(self,collObj):
        ''' get the Oriented Bounding Box '''
        # save object's parent and transformation
        parent=collObj.getParent()
        trans=collObj.getTransform()
        # ODE need everything in world's coordinate space,
        # so bring the object directly under render, but keep the transformation
        collObj.wrtReparentTo(render)
        # get the tight bounds before any rotation
        collObj.setHpr(0,0,0)
        bounds=collObj.getTightBounds()
        offset=collObj.getBounds().getCenter()-collObj.getPos()
        # bring object to it's parent and restore it's transformation
        collObj.reparentTo(parent)
        collObj.setTransform(trans)
        # (max - min) bounds
        box=bounds[1]-bounds[0]
#        print bounds[0], bounds[1]
        return [box[0],box[1],box[2]], [offset[0],offset[1],offset[2]]

class ODEbox(ODEobjbase):
    def __init__(self, world, space, realObj=None, collObj=None,
                       density=0, surfaceId=0, collideBits=0, categoryBits=0):
        if realObj==None:
           obj=collObj
        else:
           obj=realObj
           if collObj==None:
              collObj=realObj

        boundingBox, offset=self.getOBB(collObj)
        #print boundingBox, offset

##        if offset==Vec3(0):
##            fCentered=True
##        else:
##            realGeom= OdeBoxGeom(None, lengths=boundingBox)
##            self.geom = Ode.GeomTransform(space)
##           self.geom.setGeom(realGeom)
##           realGeom.setPosition(offset)
##           nonCenteredO=1
##           print 'NON-CENTERED ORIGIN'
##
##        if density:  # create body if the object is dynamic, otherwise don't
##           self.body = ode.Body(world)
##           M = ode.Mass()
##           M.setBox(density, *boundingBox)
##           if nonCenteredO:
##              M.translate(offset)

        self.geom = OdeBoxGeom(space, *boundingBox)

        if density > 0:  # create body if the object is dynamic, otherwise don't
            self.body = OdeBody(world)
            M = OdeMass()
            M.setBox(density, *boundingBox)
            self.body.setMass(M)
            self.geom.setBody(self.body)
            #self.geom.setOffsetPosition(*offset)
            #print offset
            mass = M.getMagnitude()
        else:
            mass = 0
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        # store object's properties
        self.storeProps(realObj, mass, surfaceId, collideBits, categoryBits)

class ODEcylinder(ODEobjbase):
    def __init__(self, world, space, realObj=None, collObj=None,
                       density=0, direction=3, radius=1, length=1, surfaceId=0, collideBits=0, categoryBits=0):
        if realObj==None:
           obj=collObj
        else:
           obj=realObj
           if collObj==None:
              collObj=realObj

        self.geom = OdeCylinderGeom(space, radius, length)

        if density > 0:  # create body if the object is dynamic, otherwise don't
            self.body = OdeBody(world)
            M = OdeMass()
            M.setCylinder(density, direction, radius, length)
            self.body.setMass(M)
            self.geom.setBody(self.body)
            #self.geom.setOffsetPosition(*offset)
            #print offset
            mass = M.getMagnitude()
        else:
            mass = 0
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        # store object's properties
        self.storeProps(realObj, mass, surfaceId, collideBits, categoryBits)

class ODEcylinder2(ODEobjbase):
    def __init__(self, world, space, realObj=None, collObj=None,
                       density=0, direction=3, radius=1, length=1, surfaceId=0, collideBits=0, categoryBits=0):
        if realObj==None:
           obj=collObj
        else:
           obj=realObj
           if collObj==None:
              collObj=realObj

        self.geom = OdeSphereGeom(space, radius)

        if density > 0:  # create body if the object is dynamic, otherwise don't
            self.body = OdeBody(world)
            M = OdeMass()
            M.setCylinder(density, direction, radius, length)
            self.body.setMass(M)
            self.geom.setBody(self.body)
            #self.geom.setOffsetPosition(*offset)
            #print offset
            mass = M.getMagnitude()
        else:
            mass = 0
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        # store object's properties
        self.storeProps(realObj, mass, surfaceId, collideBits, categoryBits)


class ODECappedCylinder(ODEobjbase):
    def __init__(self, world, space, realObj=None, collObj=None,
                       density=0, direction=3,radius=1, length=1, surfaceId=0, collideBits=0, categoryBits=0):
        if realObj==None:
           obj=collObj
        else:
           obj=realObj
           if collObj==None:
              collObj=realObj

        self.geom = OdeCappedCylinderGeom(space, radius, length)

        if density > 0:  # create body if the object is dynamic, otherwise don't
            self.body = OdeBody(world)
            M = OdeMass()
            M.setCapsule(density, direction, radius, length)
            self.body.setMass(M)
            self.geom.setBody(self.body)
            #self.geom.setOffsetPosition(*offset)
            #print offset
            mass = M.getMagnitude()
        else:
            mass = 0
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        # store object's properties
        self.storeProps(realObj, mass, surfaceId, collideBits, categoryBits)


class ODEsphere(ODEobjbase):
    def __init__(self, world, space, realObj=None, collObj=None,
                       density=0, surfaceId=0, collideBits=0, categoryBits=0):
        if realObj==None:
           obj=collObj
        else:
           obj=realObj
           if collObj==None:
              collObj=realObj

        boundingBox, offset=self.getOBB(collObj)
        r = boundingBox[0]/2
        self.geom = OdeSphereGeom(space, r)
        if density > 0:  # create body if the object is dynamic, otherwise don't
            self.body = OdeBody(world)
            M = OdeMass()
            M.setSphere(density, r)
            self.body.setMass(M)
            self.geom.setBody(self.body)
            mass = M.getMagnitude()
        else:
            mass = 0
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        # store object's properties
        self.storeProps(realObj, mass, surfaceId, collideBits, categoryBits)



class ODEtrimesh(ODEobjbase):
    def __init__(self, world, space, realObj=None, collObj=None,
                       mass=0, surfaceId=0, collideBits=0, categoryBits=0):
        if realObj==None:
           obj=collObj
        else:
           obj=realObj
           if collObj==None:
              collObj=realObj


        modelTrimesh = OdeTriMeshData(obj, True)
        self.geom = OdeTriMeshGeom(space, modelTrimesh)
        if mass > 0:  # create body if the object is dynamic, otherwise don't
           self.body = OdeBody(world)
           M = OdeMass()
           boundingBox, offset=self.getOBB(collObj)
           #print boundingBox
           size = max(0.01,max(boundingBox[0],boundingBox[1],boundingBox[2])/2)
           M.setSphereTotal(mass, size)
           self.body.setMass(M)
           #self.body.setGravityMode(1)
           #print M
           self.geom.setBody(self.body)
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        # store object's properties
        self.storeProps(realObj, mass, surfaceId, collideBits, categoryBits)


# make a rectangular room using boxes
def MakeRoomBoxes(minpos, maxpos, thickness):
    # six pieces
    xmid = (maxpos[0] + minpos[0]) / 2
    ymid = (maxpos[1] + minpos[1]) / 2
    zmid = (maxpos[2] + minpos[2]) / 2
    xl = (maxpos[0] - minpos[0])
    yl = (maxpos[1] - minpos[1])
    zl = (maxpos[2] - minpos[2])
    return [
        [maxpos[0]+thickness/2,ymid,zmid,thickness,yl,zl],
        [minpos[0]-thickness/2,ymid,zmid,thickness,yl,zl],
        [xmid, ymid, maxpos[2]+thickness/2, xl, yl, thickness],
        [xmid, ymid, minpos[2]-thickness/2, xl, yl, thickness],
        [xmid, maxpos[1]+thickness/2, zmid, xl, thickness, zl],
        [xmid, minpos[1]-thickness/2, zmid, xl, thickness, zl],
    ]

def MakeRoom(node,box,odeworld,collideBits,categoryBits,minpos,maxpos,thickness,sides=6):
    boxes = MakeRoomBoxes(minpos,maxpos,thickness)
    room = node.attachNewNode("roomwalls")
    objlist=[]
    for i in range(sides):
        b = boxes[i]
        x,y,z,sx,sy,sz = b
        bNP = box.copyTo(room)
        bNP.setPos(x,y,z)
        bNP.setScale(sx,sy,sz)
        b_ode = ODEbox(odeworld.world,odeworld.space,bNP, None, 0, 0, collideBits,categoryBits)
        b_ode.delRealobj()
        odeworld.AddObject(b_ode)
        objlist.append(b_ode)
    return room,objlist

class ODEWorld_Simple():
    SIMPLESPACE = 1
    HASHSPACE = 2
    def __init__(self, spacetype=SIMPLESPACE):
        major = PandaSystem.getMajorVersion()
        minor = PandaSystem.getMinorVersion()
        self.supportEvent = (major == 1 and minor > 5) or (major > 2)
        if self.supportEvent:
            self.collisionMap = {}
        self.InitODE(spacetype)
        self.listener = set()

        # debugging
        #if self.supportEvent:
        #    self.space.setCollisionEvent("ode-collision")
        #    base.accept("ode-collision", self.onCollision)
        self.count = 0
        self.totaltime1 = 0.0
        self.totaltime2 = 0.0

    #################################################
    # this functions are obsoleted, only for 1.5.4
    def setNotifier(self, object):
        self.listener.add(object)

    def removeNotifier(self, object):
        self.listener.remove(object)

    def notify(self, collisions):
        for obj in self.listener:
            obj.odeEvent(collisions)
    # this function are obsoleted, only for 1.5.4
    #################################################

    # this function is for 1.6
    def setCollisionNotifier(self, odeobject, func):
        if self.supportEvent:
            if len(self.collisionMap) == 0:
                self.space.setCollisionEvent("ode-collision")
                base.accept("ode-collision", self.onCollision)
            id = int(str(odeobject.geom).split(" ")[-1].rstrip(")"), 16)
            #print id
            self.collisionMap[id] = (odeobject, func)

    def EnableODETask(self, task=2):
        if task == 2:
            #taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation", extraArgs=[self], appendTask=True)
            taskMgr.doMethodLater(0.5, self.simulationTask2, "ODESimulation")
        elif task == 3:
            taskMgr.doMethodLater(0.5, self.simulationTask3, "ODESimulation")
        elif task == 4: # debug
            #self.stepSize = 1.0 / 40.0
            taskMgr.doMethodLater(0.5, self.simulationTask4, "ODESimulation")
        elif task == 5: # debug
            taskMgr.doMethodLater(0.5, self.simulationTask5, "ODESimulation")
        else:
            taskMgr.remove("ODESimulation")


    def InitODE(self, spacetype):
        world = OdeWorld()
        self.world = world

        # Create a space and add a contactgroup to it to add the contact joints
        if spacetype == self.SIMPLESPACE:
            space = OdeSimpleSpace()
        elif spacetype == self.HASHSPACE:
            space = OdeHashSpace()
        self.InitODEwithSpace(space)

    def InitODEwithSpace(self, space):
        space.setAutoCollideWorld(self.world)
        contactgroup = OdeJointGroup()
        space.setAutoCollideJointGroup(contactgroup)

        self.space = space
        self.contactgroup = contactgroup
        #self.objectlist = {}
        self.objectlist = set()

        # Create an accumulator to track the time since the sim
        # has been running
        # This stepSize makes the simulation run at 90 frames per second
        self.deltaTimeAccumulator = 0.0
        #self.stepSize = 1.0 / 200.0
        #self.stepSize = 1.0 / 90.0
        self.stepSize = 1.0 / 50.0
        #s = self.world.getQuickStepNumIterations()
        #self.world.setQuickStepNumIterations(1000)
        #print s

    def AddObject(self, odeobject):
        #self.objectlist[odeobject] = odeobject
        self.objectlist.add(odeobject)

    def RemoveObject(self, odeobject):
        #del self.objectlist[odeobject]
        if self.supportEvent:
            if hasattr(odeobject, "geom") and odeobject.geom in self.collisionMap:
                del self.collisionMap[odeobject.geom]
                if len(self.collisionMap) == 0:
                    self.space.setCollisionEvent("")
        self.objectlist.remove(odeobject)

    def DestroyAllObjects(self):
        if self.supportEvent:
            self.collisionMap.clear()
            self.space.setCollisionEvent("")
        for odeobject in self.objectlist:
            odeobject.destroy()
        self.objectlist.clear()

    # The task for our simulation
    def simulationTask1(self, task):
        #self.space.autoCollide() # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        cc = self.space.autoCollide() # Setup the contact joints
        if not self.supportEvent:
            # this is obsoleted, only for 1.5.4
            collisions = []
            if cc > 0:
                for i in range(cc):
                    p = Vec3(self.space.getContactData(i*3+0),self.space.getContactData(i*3+1),self.space.getContactData(i*3+2))
                    collisions.append(p)

        #for b_ode in room.balls:
        for b_ode in self.objectlist:
            if  isinstance(b_ode, ODEobjbase):
                if b_ode.isDynamic():
                    np = b_ode.realObj
                    if np != None:
                        #body = b_ode.body
                        body = b_ode.geom
                        np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
        self.contactgroup.empty() # Clear the contact joints
        if not self.supportEvent:
            self.notify(collisions)
        return task.cont


    # The task for our simulation
    def simulationTask2(self, task):
        # Set the force on the body to push it off the ridge
        # Add the deltaTime for the task to the accumulator
        self.deltaTimeAccumulator +=globalClock.getDt()
        if self.deltaTimeAccumulator < self.stepSize:
            return task.cont

        self.space.autoCollide() # Setup the contact joints
        collisions=[]
        while self.deltaTimeAccumulator > self.stepSize:
            # Remove a stepSize from the accumulator until
            # the accumulated time is less than the stepsize
            self.deltaTimeAccumulator -= self.stepSize
            # Step the simulation
            self.world.quickStep(self.stepSize)
            cc=self.space.autoCollide() # Setup the contact joints
            if not self.supportEvent:
                # this is obsoleted, only for 1.5.4
                if cc > 0:
                    for i in range(cc):
                        p = Vec3(self.space.getContactData(i*3+0),self.space.getContactData(i*3+1),self.space.getContactData(i*3+2))
                        collisions.append(p)
            break
        #cc = self.space.autoCollide() # Setup the contact joints
        for b_ode in self.objectlist:
            if isinstance(b_ode, ODEobjbase):
                if b_ode.isDynamic():
                    np = b_ode.realObj
                    if np != None:
                        #body = b_ode.body
                        body = b_ode.geom
                        np.setPosQuat(body.getPosition(), Quat(body.getQuaternion()))
                        if b_ode.mass > 0 and hasattr(b_ode, "motionfriction"):
                            v = b_ode.body.getLinearVel()
                            ma = -b_ode.motionfriction * b_ode.mass
                            b_ode.body.addForce(ma*v[0],ma*v[1],ma*v[2])
                            v = b_ode.body.getAngularVel()
                            ma = (1-b_ode.angularfriction)
                            b_ode.body.setAngularVel(ma*v[0],ma*v[1],ma*v[2])
            else:
                # a joint ?
                b_ode.Render()
        #for contact in self.contactgroup:
        #    print contact
        self.contactgroup.empty() # Clear the contact joints
        if not self.supportEvent:
            self.notify(collisions)
        return task.cont


    # The task for our simulation
    def simulationTask2Save(self, task):
        # Set the force on the body to push it off the ridge
        # Add the deltaTime for the task to the accumulator
        self.deltaTimeAccumulator +=globalClock.getDt()
        if self.deltaTimeAccumulator < self.stepSize:
            return task.cont

        self.space.autoCollide() # Setup the contact joints
        collisions=[]
        while self.deltaTimeAccumulator > self.stepSize:
            # Remove a stepSize from the accumulator until
            # the accumulated time is less than the stepsize
            self.deltaTimeAccumulator -= self.stepSize
            # Step the simulation
            self.world.quickStep(self.stepSize)
            cc=self.space.autoCollide() # Setup the contact joints
            if not self.supportEvent:
                # this is obsoleted, only for 1.5.4
                if cc > 0:
                    for i in range(cc):
                        p = Vec3(self.space.getContactData(i*3+0),self.space.getContactData(i*3+1),self.space.getContactData(i*3+2))
                        collisions.append(p)

        #cc = self.space.autoCollide() # Setup the contact joints
        for b_ode in self.objectlist:
            if isinstance(b_ode, ODEobjbase):
                if b_ode.isDynamic():
                    np = b_ode.realObj
                    if np != None:
                        #body = b_ode.body
                        body = b_ode.geom
                        np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
                        if b_ode.mass > 0 and hasattr(b_ode, "motionfriction"):
                            v = b_ode.body.getLinearVel()
                            ma = -b_ode.motionfriction * b_ode.mass
                            b_ode.body.addForce(ma*v[0],ma*v[1],ma*v[2])
                            v = b_ode.body.getAngularVel()
                            ma = (1-b_ode.angularfriction)
                            b_ode.body.setAngularVel(ma*v[0],ma*v[1],ma*v[2])
            else:
                # a joint ?
                b_ode.Render()
        #for contact in self.contactgroup:
        #    print contact
        self.contactgroup.empty() # Clear the contact joints
        if not self.supportEvent:
            self.notify(collisions)
        return task.cont

    def simulationTask3(self,task):
        iterations = 5
        #We limit the maximum time not to receive explosion of physic system if application stuck
        dt=globalClock.getDt()
        if dt>0.02: dt=0.02
        dt=dt / iterations * 3

        #Some iterations for the more stable simulation
        for i in xrange(iterations):
          self.world.quickStep(dt)
          cc=self.space.autoCollide()
        #Sync the box with the bodies
        for b_ode in self.objectlist:
            if isinstance(b_ode, ODEobjbase):
                if b_ode.isDynamic():
                    np = b_ode.realObj
                    if np != None:
                        #body = b_ode.body
                        body = b_ode.geom
                        np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
                        if b_ode.mass > 0 and hasattr(b_ode, "motionfriction"):
                            v = b_ode.body.getLinearVel()
                            ma = -b_ode.motionfriction * b_ode.mass
                            b_ode.body.addForce(ma*v[0],ma*v[1],ma*v[2])
                            v = b_ode.body.getAngularVel()
                            ma = (1-b_ode.angularfriction)
                            b_ode.body.setAngularVel(ma*v[0],ma*v[1],ma*v[2])
            else:
                # a joint ?
                b_ode.Render()
        self.contactgroup.empty()
        return task.cont


    # Setup collision event
    def onCollision(self, entry):
        geom1 = entry.getGeom1()
        geom2 = entry.getGeom2()
        id1 = int(str(geom1).split(" ")[-1].rstrip(")"), 16)
        id2 = int(str(geom2).split(" ")[-1].rstrip(")"), 16)
        if id1 in self.collisionMap:
            id = id1
            geomn = geom2
        elif id2 in self.collisionMap:
            id = id2
            geomn = geom1
        else:
            return
        odeobject, func = self.collisionMap[id]
        func(odeobject, geomn, entry)
        #points = entry.getContactPoints()
        #body1 = entry.getBody1()
        #body2 = entry.getBody2()


    # The debug task for performance test
    def simulationTask4(self, task):
        # Set the force on the body to push it off the ridge
        # Add the deltaTime for the task to the accumulator
        self.deltaTimeAccumulator +=globalClock.getDt()
        if self.deltaTimeAccumulator < self.stepSize:
            return task.cont

        #self.space.autoCollide() # Setup the contact joints
        collisions=[]
        while self.deltaTimeAccumulator > self.stepSize:
            # Remove a stepSize from the accumulator until
            # the accumulated time is less than the stepsize
            self.deltaTimeAccumulator -= self.stepSize
            # Step the simulation
            t1 = time.time()
            #for i in range(100):
            self.world.quickStep(self.stepSize)
            t12 = time.time()
            t2 = time.time()
            cc = self.space.autoCollide() # Setup the contact joints
            t22 = time.time()
            self.count += 1
            self.totaltime1 += t12 - t1
            self.totaltime2 += t22 - t2
            #print t2,t1
            #cc=self.space.autoCollide() # Setup the contact joints
            if self.count > 200:
                print "quickStep %f %0.3f" % (self.totaltime1, self.totaltime1 * 1000 / self.count)
                print "autocollide %f %0.3f" % (self.totaltime2, self.totaltime2 * 1000 / self.count)
                #print "cc %0.1f" % (self.totaltime2 / self.count)
                self.count = 0
                self.totaltime1 = 0.0
                self.totaltime2 = 0.0
            #if not self.supportEvent:
                # this is obsoleted, only for 1.5.4
            #    if cc > 0:
            #        for i in range(cc):
            #            p = Vec3(self.space.getContactData(i*3+0),self.space.getContactData(i*3+1),self.space.getContactData(i*3+2))
            #            collisions.append(p)

        #cc = self.space.autoCollide() # Setup the contact joints
        if True:
            for b_ode in self.objectlist:
                if isinstance(b_ode, ODEobjbase):
                    if b_ode.isDynamic():
                        np = b_ode.realObj
                        if np != None:
                            #body = b_ode.body
                            body = b_ode.geom
                            #np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
                            np.setPosQuat(body.getPosition(), Quat(body.getQuaternion()))
                            if False and b_ode.mass > 0 and hasattr(b_ode, "motionfriction"):
                                v = b_ode.body.getLinearVel()
                                ma = -b_ode.motionfriction * b_ode.mass
                                b_ode.body.addForce(ma*v[0],ma*v[1],ma*v[2])
                                v = b_ode.body.getAngularVel()
                                ma = (1-b_ode.angularfriction)
                                b_ode.body.setAngularVel(ma*v[0],ma*v[1],ma*v[2])
                else:
                    # a joint ?
                    b_ode.Render()
        #for contact in self.contactgroup:
        #    print contact
        self.contactgroup.empty() # Clear the contact joints
        if not self.supportEvent:
            self.notify(collisions)
        return task.cont

    # The task for our simulation
    def simulationTask5(self, task):
        # Set the force on the body to push it off the ridge
        # Add the deltaTime for the task to the accumulator
        self.deltaTimeAccumulator +=globalClock.getDt()
        if self.deltaTimeAccumulator < self.stepSize:
            return task.cont

        collisions=[]
        while self.deltaTimeAccumulator > self.stepSize:
            # Remove a stepSize from the accumulator until
            # the accumulated time is less than the stepsize
            self.deltaTimeAccumulator -= self.stepSize
            # Step the simulation
            self.space.autoCollide() # Setup the contact joints
            self.world.quickStep(self.stepSize)

        for b_ode in self.objectlist:
            if isinstance(b_ode, ODEobjbase):
                if b_ode.isDynamic():
                    np = b_ode.realObj
                    if np != None:
                        #body = b_ode.body
                        body = b_ode.geom
                        np.setPosQuat(body.getPosition(), Quat(body.getQuaternion()))
                        #if b_ode.mass > 0 and hasattr(b_ode, "motionfriction"):
                        #    v = b_ode.body.getLinearVel()
                        #    ma = -b_ode.motionfriction * b_ode.mass
                        #    b_ode.body.addForce(ma*v[0],ma*v[1],ma*v[2])
                        #    v = b_ode.body.getAngularVel()
                        #    ma = (1-b_ode.angularfriction)
                        #    b_ode.body.setAngularVel(ma*v[0],ma*v[1],ma*v[2])
            else:
                # a joint ?
                b_ode.Render()
        #for contact in self.contactgroup:
        #    print contact
        self.contactgroup.empty() # Clear the contact joints
        if not self.supportEvent:
            self.notify(collisions)
        return task.cont


class ODEWorld_AutoHash(ODEWorld_Simple):
    def __init__(self):
        ODEWorld_Simple.__init__(self, ODEWorld_Simple.HASHSPACE)

