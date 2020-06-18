
"""
Raw files can be opened with e.g. Paint Shop Pro. With the NVIDIA plugin the
image can be saved in the in the DDS format. Normalizing is possible as well:

http://developer.nvidia.com/object/photoshop_dds_plugins.html
"""

import random

# width and height in pixels
N = 256

f = open("noise.raw", "wb")
for y in range(N):
	for x in range(N):
		color1 = random.randint(0, 255)
		color2 = random.randint(0, 255)
		color3 = random.randint(0, 255)
		f.write(chr(color1) + chr(color2) + chr(color3))
