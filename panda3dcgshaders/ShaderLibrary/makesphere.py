
"""
Creating a sphere based on random spherical coordinates is not the best idea
(UVsphere called in Blender), because the resulting vertexes are not distributed
evenly (most vertexes are located around two poles).

Creating a sphere from a Icosahedron, called a Icosasphere (unfortunately
IcoSphere in Blender), is a better idea.

http://en.wikipedia.org/wiki/Icosasphere
http://en.wikipedia.org/wiki/Golden_ratio
http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html

The script create a sphere.obj file. This is just there to test, if the
generated coordinates are correct at all-
"""

import random
import math

# subdivions
N = 1

def mid(v1, v2):
	m0 = (v1[0] + v2[0]) / 2.0
	m1 = (v1[1] + v2[1]) / 2.0
	m2 = (v1[2] + v2[2]) / 2.0
	return (m0, m1, m2)

def normalize(v):
	length = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) ** 0.5
	return (v[0] / length, v[1] / length, v[2] / length)

x = (1.0 + math.sqrt(5.0)) / 2.0

vertexes = []
vertexes +=  [ (-1, x, 0) ]
vertexes +=  [ (1, x, 0) ]
vertexes +=  [ (-1, -x, 0) ]
vertexes +=  [ (1, -x, 0) ]
vertexes +=  [ (0, -1, x) ]
vertexes +=  [ (0, 1, x) ]
vertexes +=  [ (0, -1, -x) ]
vertexes +=  [ (0, 1, -x) ]
vertexes +=  [ (x, 0, -1) ]
vertexes +=  [ (x, 0, 1) ]
vertexes +=  [ (-x, 0, -1) ]
vertexes +=  [ (-x, 0, 1) ]

triangles = []
triangles += [ (0, 11, 5) ]
triangles += [ (0, 5, 1) ]
triangles += [ (0, 1, 7) ]
triangles += [ (0, 7, 10) ]
triangles += [ (0, 10, 11) ]
triangles += [ (1, 5, 9) ]
triangles += [ (5, 11, 4) ]
triangles += [ (11, 10, 2) ]
triangles += [ (10, 7, 6) ]
triangles += [ (7, 1, 8) ]
triangles += [ (3, 9, 4) ]
triangles += [ (3, 4, 2) ]
triangles += [ (3, 2, 6) ]
triangles += [ (3, 6, 8) ]
triangles += [ (3, 8, 9) ]
triangles += [ (4, 9, 5) ]
triangles += [ (2, 4, 11) ]
triangles += [ (6, 2, 10) ]
triangles += [ (8, 6, 7) ]
triangles += [ (9, 8, 1) ]

for n in range(N):
	count = 0
	newtriangles = []
	newvertexes = []
	for triangle in triangles:
		v0 = vertexes[triangle[0]]
		v1 = vertexes[triangle[1]]
		v2 = vertexes[triangle[2]]

		v01 = mid(v0, v1)
		v02 = mid(v0, v2)
		v12 = mid(v1, v2)
		newvertexes += [ v0 ]
		newvertexes += [ v1 ]
		newvertexes += [ v2 ]
		newvertexes += [ v01 ]
		newvertexes += [ v02 ]
		newvertexes += [ v12 ]

		c0 = count + 0
		c1 = count + 1
		c2 = count + 2
		c01 = count + 3
		c02 = count + 4
		c12 = count + 5
		newtriangles += [ (c0, c02, c01) ]
		newtriangles += [ (c1, c01, c12) ]
		newtriangles += [ (c2, c12, c02) ]
		newtriangles += [ (c01, c02, c12) ]

		count += 6

	vertexes = newvertexes
	triangles = newtriangles

f = open("sphere.obj", "wb")
for vertex in vertexes:
	f.write("v %f %f %f\n" % normalize(vertex))
for triangle in triangles:
	f.write("f %i %i %i\n" % (triangle[0] + 1, triangle[1] + 1, triangle[2] + 1))

print "float3 sphere[] = {"
for vertex in vertexes:
	r = random.random()
	print "\tfloat3(%f, %f, %f)," % (vertex[0] * r, vertex[1] * r, vertex[2] * r)
print "};"
