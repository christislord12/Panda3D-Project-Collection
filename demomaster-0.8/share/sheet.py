# code from dinoint
# http://panda3d.org/phpbb2/viewtopic.php?t=5558
from pandac.PandaModules import NodePath, SheetNode, NurbsSurfaceEvaluator
from pandac.PandaModules import VBase3, Point3

class Sheet(NodePath):

##    showSheet = base.config.GetBool('show-sheet', 1)

    def __init__(self, name="sheet"):
        self.sheetNode = SheetNode(name)
        self.surface = NurbsSurfaceEvaluator()
        self.sheetNode.setSurface(self.surface)
        self.sheetNode.setUseVertexColor(True)
        NodePath.__init__(self, self.sheetNode)
        self.name = name

    def setup(self, uOrder, vOrder, uVertsNum, verts, uKnots=None, vKnots=None):

        self.uOrder = uOrder
        self.vOrder = vOrder
        self.verts = verts

        self.uVertsNum =  uVertsNum
        self.vVertsNum = len(self.verts) / self.uVertsNum

        self.uKnots = uKnots
        self.vKnots = vKnots

        self.recompute()

    def recompute(self):
##        if not self.showSheet:
##            return

        numVerts = len(self.verts)
        #self.surface.reset(numVerts, numVerts)
        self.surface.reset(self.uVertsNum, self.vVertsNum)
        self.surface.setUOrder(self.uOrder)
        self.surface.setVOrder(self.vOrder)

        defaultNodePath = None
        defaultPoint = (0, 0, 0)
        defaultColor = (1, 1, 1, 1)

        useVertexColor = self.sheetNode.getUseVertexColor()
        # this function exists for ropeNode but not for sheetNode ?
        vcd = 0 #self.sheetNode.getVertexColorDimension()

        idx = 0
        for v in range(self.vVertsNum):
            for u in range(self.uVertsNum):
                vertex = self.verts[idx]
                if isinstance(vertex, tuple):
                    nodePath, point = vertex
                    color = defaultColor
                else:
                    nodePath = vertex.get('node', defaultNodePath)
                    point = vertex.get('point', defaultPoint)
                    color = vertex.get('color', defaultColor)

                if isinstance(point, tuple):
                    if (len(point) >= 4):
                        self.surface.setVertex(u, v, \
                                    VBase4(point[0], point[1], point[2], point[3]))
                    else:
                        self.surface.setVertex(u, v, \
                                               VBase3(point[0], point[1], point[2]))
                else:
                    self.surface.setVertex(u, v, point)
                if nodePath:
                    self.surface.setVertexSpace(u, v, nodePath)
                if useVertexColor:
                    self.surface.setExtendedVertex(u, v, vcd + 0, color[0])
                    self.surface.setExtendedVertex(u, v, vcd + 1, color[1])
                    self.surface.setExtendedVertex(u, v, vcd + 2, color[2])
                    self.surface.setExtendedVertex(u, v, vcd + 3, color[3])
                idx +=1

        if self.uKnots != None:
            for i in range(len(self.uKnots)):
                self.surface.setUKnot(i, self.uKnots[i])

        if self.vKnots != None:
            for i in range(len(self.vKnots)):
                self.surface.setVKnot(i, self.vKnots[i])

        self.sheetNode.resetBound(self)


    def normalize(self, uKnots = True, vKnots = True):
        if uKnots:
            self.surface.normalizeUKnots()
        if vKnots:
            self.surface.normalizeVKnots()


    def getPoints(self, len):
        result = self.surface.evaluate(self)
        numPts = len
        sheetPts = []
        for i in range(numPts):
            pt = Point3()
            u = v = i / float(numPts -1)
            result.evalPoint(u,v, pt)
            sheetPts.append(pt)
        return sheetPts

