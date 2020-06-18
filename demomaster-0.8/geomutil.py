import math
from pandac.PandaModules import NodePath, Filename
from pandac.PandaModules import CardMaker
from pandac.PandaModules import GeomVertexFormat, GeomVertexData
from pandac.PandaModules import Geom, GeomTriangles, GeomVertexWriter,GeomVertexReader
from pandac.PandaModules import Texture, GeomNode, Vec3, Point2
from pandac.PandaModules import EggData,EggVertexPool,EggPolygon,EggVertex,loadEggData,Point3D,Point2D,Vec3D,deg2Rad,LineSegs
from pandac.PandaModules import CSZupRight

##def createPlane(name, width, height, numXSegments, numYSegments):
##    maker = CardMaker( 'grid' )
##    maker.setFrame( 0, float(width)/numXSegments, 0, float(height)/numYSegments)
##    np = NodePath(name)
##    dx = 1.0 / numXSegments
##    dy = 1.0 / numXSegments
##    u = 0.0
##    lx = -float(width)/2
##    for x in range(numXSegments):
##        v = 0.0
##        ly = -float(height)/2
##        for y in range(numYSegments):
##            maker.setUvRange(Point2(u,v), Point2(u+dx,v+dy))
##            v += dy
##            node = np.attachNewNode(maker.generate())
##            node.setHpr(0,-90,0)
##            node.setPos(lx, ly, 0)
##            ly += float(height)/numYSegments
##        u += dx
##        lx += float(width)/numXSegments
##    print lx,ly
##    np.flattenStrong()
##    return np

def createPlane(name, width, height, numXSegments, numYSegments):
    maker = CardMaker( 'grid' )
    maker.setFrame( 0, 1, 0, 1)
    np = NodePath(name)
    dx = 1.0 / numXSegments
    dy = 1.0 / numXSegments
    u = 0.0
    for x in range(numXSegments):
        v = 0.0
        for y in range(numYSegments):
            maker.setUvRange(Point2(u,v), Point2(u+dx,v+dy))
            v += dy
            node = np.attachNewNode(maker.generate())
            node.setHpr(0,-90,0)
            node.setPos(float(x) -float(numXSegments)/2, float(y)-float(numYSegments)/2, 0)
        u += dx
    np.setScale(float(width)/numXSegments, float(height)/numYSegments, 1)
    np.flattenStrong()
    return np


def createCube(name='Cube'):
    #you cant normalize in-place so this is a helper function
    def myNormalize(myVec):
    	myVec.normalize()
    	return myVec

    #helper function to make a square given the Lower-Left-Hand and Upper-Right-Hand corners
    def makeSquare(x1,y1,z1, x2,y2,z2):
    	format=GeomVertexFormat.getV3n3cpt2()
    	vdata=GeomVertexData('square', format, Geom.UHDynamic)

    	vertex=GeomVertexWriter(vdata, 'vertex')
    	normal=GeomVertexWriter(vdata, 'normal')
    	color=GeomVertexWriter(vdata, 'color')
    	texcoord=GeomVertexWriter(vdata, 'texcoord')

    	#make sure we draw the sqaure in the right plane
    	if x1!=x2:
    		vertex.addData3f(x1, y1, z1)
    		vertex.addData3f(x2, y1, z1)
    		vertex.addData3f(x2, y2, z2)
    		vertex.addData3f(x1, y2, z2)

      		normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
       		normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y1-1, 2*z1-1)))
       		normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
       		normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y2-1, 2*z2-1)))

    	else:
    		vertex.addData3f(x1, y1, z1)
    		vertex.addData3f(x2, y2, z1)
    		vertex.addData3f(x2, y2, z2)
    		vertex.addData3f(x1, y1, z2)

    		normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
    		normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z1-1)))
    		normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
    		normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z2-1)))

    	#adding different colors to the vertex for visibility
    	color.addData4f(1.0,0.0,0.0,1.0)
    	color.addData4f(0.0,1.0,0.0,1.0)
    	color.addData4f(0.0,0.0,1.0,1.0)
    	color.addData4f(1.0,0.0,1.0,1.0)

    	texcoord.addData2f(0.0, 1.0)
    	texcoord.addData2f(0.0, 0.0)
    	texcoord.addData2f(1.0, 0.0)
    	texcoord.addData2f(1.0, 1.0)

    	#quads arent directly supported by the Geom interface
    	#you might be interested in the CardMaker class if you are
    	#interested in rectangle though
    	tri1=GeomTriangles(Geom.UHDynamic)
    	tri2=GeomTriangles(Geom.UHDynamic)

    	tri1.addVertex(0)
    	tri1.addVertex(1)
    	tri1.addVertex(3)

    	tri2.addConsecutiveVertices(1,3)

    	tri1.closePrimitive()
    	tri2.closePrimitive()


    	square=Geom(vdata)
    	square.addPrimitive(tri1)
    	square.addPrimitive(tri2)

    	return square

    square0=makeSquare(-1,-1,-1, 1,-1, 1)
    square1=makeSquare(-1, 1,-1, 1, 1, 1)
    square2=makeSquare(-1, 1, 1, 1,-1, 1)
    square3=makeSquare(-1, 1,-1, 1,-1,-1)
    square4=makeSquare(-1,-1,-1,-1, 1, 1)
    square5=makeSquare( 1,-1,-1, 1, 1, 1)
    snode=GeomNode('square')
    snode.addGeom(square0)
    snode.addGeom(square1)
    snode.addGeom(square2)
    snode.addGeom(square3)
    snode.addGeom(square4)
    snode.addGeom(square5)
    np = NodePath(snode)
    #np = render.attachNewNode(snode)
    #np.setScale(0.5)
    #np.flattenLight() # cannot be flattened, otherwise the vertex color will be gone
    np.setTwoSided(True) # looks like the tutorial code has a bug ? need to correct the normal ?
    return np


# code from drwr http://panda3d.etc.cmu.edu/phpbb2/viewtopic.php?t=374
def makeArc(angleDegrees = 360, numSteps = 16, thickness=5):
    ls = LineSegs()
    angleRadians = deg2Rad(angleDegrees)

    for i in range(numSteps + 1):
        a = angleRadians * i / numSteps
        y = math.sin(a)
        x = math.cos(a)

        ls.drawTo(x, y, 0)

    #ls.setColor(Vec4(1,1,1,1))
    ls.setThickness(thickness)
    node = ls.create()
    return NodePath(node)

# code from drwr http://panda3d.etc.cmu.edu/phpbb2/viewtopic.php?t=374
def makeEggWedge(angleDegrees = 360, numSteps = 16):

        data = EggData()

        vp = EggVertexPool('fan')
        data.addChild(vp)

        poly = EggPolygon()
        data.addChild(poly)

        v = EggVertex()
        v.setPos(Point3D(0, 0, 0))
        poly.addVertex(vp.addVertex(v))

        angleRadians = deg2Rad(angleDegrees)

        for i in range(numSteps + 1):
            a = angleRadians * i / numSteps
            y = math.sin(a)
            x = math.cos(a)

            v = EggVertex()
            v.setPos(Point3D(x, y, 0))
            v.setNormal(Vec3D(0,0,1))
            poly.addVertex(vp.addVertex(v))

        node = loadEggData(data)
        return NodePath(node)


def addSquare( data, vp, x, y, w, h, texCoord = [[1,0],[1,1],[0,1],[0,0]] ):
    epoly = EggPolygon()
    data.addChild(epoly)
    in_position = []
    in_position.append([x,y,0])
    in_position.append([x+w,y,0])
    in_position.append([x+w,y+h,0])
    in_position.append([x,y+h,0])
    #print in_position
    for i in range(4):
        ev = EggVertex()
        ev.setPos(Point3D(*in_position[i]))
        ev.setUv(Point2D(*texCoord[i]))
        ev.setNormal(Vec3D(0,0,1))
        #ev.setColor(VBase4(*in_color[i]))
        epoly.addVertex(vp.addVertex(ev))

def makeEggPlane(width, height, numXSegments, numYSegments, filename=None):

        data = EggData()
        vp = EggVertexPool('s')
        data.addChild(vp)

        width = float(width)
        height = float(height)

        dwidth = (width) /numXSegments
        dheight = (height)/numYSegments
        #addSquare( data, vp, 0, 0, width/2, height/2)
        #addSquare( data, vp, width/2, height/2, width/2, height/2)
##        v = EggVertex()
        dy = 1.0 / numYSegments
        dx = 1.0 / numXSegments
        for y in range(numYSegments):
            ty = 1.0 - y * dy
            for x in range(numXSegments):
                tx = x * dx
                xpos = float(x) * dwidth - width / 2.0
                ypos = float(y) * dheight - height / 2.0
                texCoord = [[tx,ty],[tx+dx,ty],[tx+dx,ty-dy],[tx,ty-dy]]
                addSquare( data, vp, xpos, ypos, dwidth, dheight, texCoord)

        if filename != None:
            data.setCoordinateSystem(CSZupRight)
            data.writeEgg(Filename(filename))
        node = loadEggData(data)
        return NodePath(node)

def getVertexInfo(np, relative=None):
    vertexinfo = []
    geomnode = np.node()
    nrgeoms = geomnode.getNumGeoms()
    for n in range(nrgeoms):
        geom = geomnode.getGeom(n)
        data = geom.getVertexData()
        numVtx = data.getNumRows()
        vtxReader=GeomVertexReader(data)
        # begin reading at vertex 0
        vtxReader.setRow(0)
        # get the vertex position column
        column=-1
        columnName=''
        while ( columnName!='vertex' ):
            column+=1
            vtxReader.setColumn(column)
            columnName=str(vtxReader.getColumn().getName())
        #=========================================================
        # create vertex normal reader
        normalReader=GeomVertexReader(data)
        # begin reading at vertex 0
        normalReader.setRow(0)
        # get the vertex normal column
        hasNormals=True
        column=-1
        columnName=''
        while ( columnName!='normal' ):
           column+=1
           normalReader.setColumn(column)
           if normalReader.getColumn()==None:
               hasNormals=False
               break
           else:
               columnName=str(normalReader.getColumn().getName())

        for i in range(numVtx):
            vtx = vtxReader.getData3f()
            if relative != None:
                vtx=relative.getRelativePoint(np,vtx)

            normal=normalReader.getData3f()
            if relative != None:
                normal=relative.getRelativeVector(np,normal)
            vertexinfo.append((vtx,normal))
        break
    return vertexinfo
