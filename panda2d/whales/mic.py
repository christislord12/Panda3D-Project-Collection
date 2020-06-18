# -*- coding: utf-8 -*-

import mic_panda
import mic_alsa
import mic_pyaudio

#binds, this will suck i know
CAN = False
NAME = "none"
if mic_panda.CAN :
	CAN = True
	print "Imported Panda Mic"
	from mic_panda import *
elif mic_alsa.CAN:
	CAN = True
	print "Imported Alsa"
	from mic_alsa import *
elif mic_pyaudio.CAN :
	CAN = True
	print "Imported PyAudio"
	from mic_pyaudio import  *

