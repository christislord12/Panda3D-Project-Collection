#!/usr/bin/python
## This is an example of a simple sound capture script.
##
## The script opens an ALSA pcm for sound capture. Set
## various attributes of the capture, and reads in a loop,
## Then prints the volume.
##
## To test it out, run it and shout at your microphone:

import alsaaudio, time, audioop
RATE = 8000
# Open the device in nonblocking capture mode. The last argument could
# just as well have been zero for blocking mode. Then we could have
# left out the sleep call in the bottom of the loop
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL) #PCM_NONBLOCK

# Set attributes: Mono, 8000 Hz, 16 bit little endian samples
inp.setchannels(2)
inp.setrate(RATE)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE) #PCM_FORMAT_S16_LE

# The period size controls the internal number of frames per period.
# The significance of this parameter is documented in the ALSA api.
# For our purposes, it is suficcient to know that reads from the device
# will return this many frames. Each frame being 2 bytes long.
# This means that the reads below will return either 320 bytes of data
# or 0 bytes of data. The latter is possible because we are in nonblocking
# mode.
inp.setperiodsize(RATE/2)



from numpy import fft
import numpy as np

from struct import unpack
import matplotlib.pyplot as plt

from panda3d.core import Filename, PNMImage, Texture, Vec4, CardMaker
import direct.directbase.DirectStart
cm = CardMaker('card')
cm.setFrameFullscreenQuad()
card = render2d.attachNewNode(cm.generate())
mypnm= PNMImage(64,64)
myTexture = Texture()
myTexture.load(mypnm)
card.setTexture(myTexture,1)
def analyzeBurst(inArray,ssp):
    """ returns an array containing different kinds of information on the waveform you throw into,
    requires an array as input, and the samples per second,for now that's [peakamplitude,bass-amplitude,index of the frequency with max amplitude]
    given the main class defaults last value can be multiplied by 50 and you have the Hz number.
    """    
    outarray= fft.rfft(inArray)[:len(inArray)/2]  #the splitting is only done cause the rfft returns symetrical results. we dont need the right half
    freq= fft.fftfreq(len(inArray),1./ssp)[:len(inArray)/2] #contains the frequency in Hz
    #outarray = np.abs(outarray) # this array contains the amplitude for each frequency in the array above.
    #print freq,outarray
    #peak=np.ptp(inArray)
    #bass= np.sum(outarray[1:3])# np.sum(outarray[1:3]) #that makes frequencies 50,100 and 150  hz
    #freqpeak= np.argmax(outarray[10:50])
    return outarray,freq
    #return [peak,freqpeak,bass,outarray]


def myFunction(task):
    global card
    global myTexture
    global mypnm
    # Read data from device
    #print "\nnewblock"
    l,data = inp.read()
    #print len(data)
    channels =[]
    amps = []
    c = 340 #m/s speed
    d = 0.07 # 7cm for my mics
    if len(data)==680:
        rawdata = unpack( "<"+("h"*l*2),data) #unpack the rawdata into a list of int's
        for j in range(2):
            data= np.array(rawdata)[j::2]/float(1<<16)  #untangle-channels
            analyzedData,freqs = analyzeBurst(data,8000)
            wavelength = c/freqs
            channels.append(np.angle(analyzedData,deg=1))
            amps.append(np.abs(analyzedData))
        phasediff = channels[0]-channels[1]
        distS = ((phasediff/360) *wavelength)/d
        direction =  np.rad2deg( np.arccos( distS))
        #print direction
        plt.plot(direction-90, amps[0])
        plt.axis('tight')
        #plt.show()
        mypnm.fill(0)
        for i in range(0,63):
            mypnm.setGreen(32,i,.5)
        for x,angle in enumerate(direction):
            
            if 0<angle<180:
                #print x,angle,int(amps[0][x]),int(amps[1][x]),angle
                if amps[0][x]*10 > 63:
                    amps[0][x] = 6.3
                if amps[1][x]*10 > 63:
                    amps[1][x] = 6.3
                mypnm.setRed(  int(angle*63/180),int(amps[0][x]*10),1 )
                mypnm.setBlue( int(angle*63/180),int(amps[1][x]*10),1 )
                """
                for i in range(0,int(amps[0][x]*30)):
                    if i>63:
                        i=63
                    mypnm.setGreen(int(angle*63/180),63-i,1)
                for i in range(0,int(amps[1][x]*30)):
                    if i>63:
                        i=63
                    mypnm.setRed(int(angle*63/180),63-i,1)
                """
        myTexture.load(mypnm)
    else:
        pass
    return task.again
 
myTask = taskMgr.add(myFunction, 'awesometask')
run()
