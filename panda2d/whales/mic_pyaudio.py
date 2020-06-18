CAN = False
try:
	import pyaudio
	import numpy as np
	CAN = True
except Exception, e:
	print (e)

NAME = "pyaudio"

import wave
import sys
from Queue import Queue
from threading import Thread


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
STREAM = None #globals :)

import subprocess as s
import threading
from Queue import Queue #python2
class StopThread(threading.Thread):
	"""Thread class with a stop() method. The thread itself has to check
	regularly for the stopped() condition."""

	def __init__(self):
		super(StopThread, self).__init__()
		self._stop = threading.Event()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

class Reader(StopThread):
	def __init__(self):
		StopThread.__init__(self)
		self.q = Queue()
		self.p = pyaudio.PyAudio()
		RATE = int(self.p.get_device_info_by_index(0)['defaultSampleRate'])
		print("my rate is ", RATE)
		self.str = self.p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

		self.window = np.blackman(CHUNK)


	def read(self):
		try:
			#this is extremely dangerous
			data = self.str.read(CHUNK)
			# unpack the data and times by the hamming window
			#indata = np.array(wave.struct.unpack("%dh"%(CHUNK), data))*self.window
			indata = np.fromstring(data, dtype=np.int16)
			p = 20*np.log10(np.abs(np.fft.rfft(indata))) #power ?
			f = np.linspace(0, RATE/2.0, len(p)) #freqs?
			pmi = len(p) - 1 - p[::-1].argmax() #to get the last big freq (not 0)
			pm = p[pmi]
			if(f[pmi]< 0.001) or np.isinf(pm): return (-1, -1)
			return (f[pmi], pm)
		except Exception, e:
			if isinstance(e, KeyboardInterrupt): raise e
			print("error reading audio", e)
			return (-1, -1)


	def read_(self):
		#this is extremely dangerous
		data = self.str.read(CHUNK)
		# unpack the data and times by the hamming window
		#indata = np.array(wave.struct.unpack("%dh"%(CHUNK), data))*self.window
		indata = np.fromstring(data, dtype=np.int16)
		# Take the fft and square each value
		fftData = abs(np.fft.rfft(indata))**2
		# find the maximum
		which = fftData[1:].argmax() + 1
		# use quadratic interpolation around the max
		thefreq = 0
		if which != len(fftData)-1:
			y0,y1,y2 = np.log(fftData[which-1:which+2:])
			x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
		else:
			x1 = 0

		# we love premature optimization
		# find the frequency and output it
		thefreq = (which + x1) * RATE / CHUNK
		mean1 = indata.max(axis=0)

		return (thefreq, mean1)

	def run(self):
		while not self.stopped():
			self.q.put(self.read())
		self.stop()
		print ("im dead")


	def kill(self):
		self.str.stop_stream()
		self.str.close()
		self.p.terminate()

READER = None
def open():
	global READER
	READER = Reader()
	READER.start()

def tell():
	global READER
	if not READER or READER.stopped(): return
	fq = (-1.0, -1.0)
	try:
		s = READER.q.qsize()
		while(s):
			try:
				READER.q.get(False)
			except: pass
			s -= 1
		fq = READER.q.get(True, 0.1)
	#doesnt need a loop for out because it has no limit
	except:
		pass
	return fq

def die():
	if not READER or READER.stopped(): return
	READER.stop()
	READER.kill()

def _open():
	global STREAM
	p = pyaudio.PyAudio()
	STREAM = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

def _read():
	if not STREAM : return
	data = STREAM.read(CHUNK)
	# unpack the data and times by the hamming window
	return np.array(wave.struct.unpack("%dh"%(CHUNK), data))*window

def _tell():
	if not STREAM : return
	data = STREAM.read(CHUNK)
	# unpack the data and times by the hamming window
	indata = np.array(wave.struct.unpack("%dh"%(CHUNK), data))*window
	#np.fromstring(data, dtype=np.int16)
	# Take the fft and square each value
	fftData=abs(np.fft.rfft(indata))**2
	# find the maximum
	which = fftData[1:].argmax() + 1
	# use quadratic interpolation around the max
	thefreq = 0
	if which != len(fftData)-1:
		y0,y1,y2 = np.log(fftData[which-1:which+2:])
		x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
	else:
		x1 = 0

	# we love premature optimization
	# find the frequency and output it
	thefreq = (which + x1) * RATE / CHUNK
	return thefreq

def start():
	worker = Thread(target=tRead, args=(_q,))
	worker.setDaemon(True)
	worker.start()


def test ():
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	RECORD_SECONDS = 5
	WAVE_OUTPUT_FILENAME = "output.wav"

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

	print("* recording")

	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	#well this works perfectly