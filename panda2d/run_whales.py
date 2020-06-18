# -*- coding: utf-8 -*-
#Copyright 2015 Jerónimo Barraco Mármol - moongate.com.ar GPLv3 moongate.com.ar
from whales.main import runWorld
import sys
#works only when you interrup using CTRL-C
try:
	runWorld()
except KeyboardInterrupt:
	sys.exit(0)
##### POLISHING THE CODE!
##### (after the ggj)
