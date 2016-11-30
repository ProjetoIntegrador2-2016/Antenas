import numpy as np
import sys
import subprocess
from struct import *
import serial
import time
import atexit
import threading
import library2


ADPT1 = "wlan1" #right
ADPT2 = "wlan2" #left
FORWARD = 'f'
RIGHT = 'r'
LEFT = 'l'
KERNEL_SIZE = 101


media1 = 0
numwlan1 = 1
soma1= 0
media2 = 0
numwlan2 = 1
soma2 = 0



class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self,size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max
        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

    def append(self,x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data
        

def calcMediaOfSignal1(wlan1):
	global media1
	global numwlan1
	global soma1 
	media1 = (wlan1+soma1)/numwlan1
	
	
def calcMediaOfSignal2(wlan2):	
	global media2
	global numwlan2
	global soma2
	media2 = (wlan2+soma2)/numwlan2


def main():    
	
	ser = serial.Serial('/dev/ttyAMA0', 19200, timeout=1)
    
	buffAbs = RingBuffer(KERNEL_SIZE)
	buffSgn = RingBuffer(KERNEL_SIZE)
	buffwlan1 = RingBuffer(KERNEL_SIZE)
	buffwlan2 = RingBuffer(KERNEL_SIZE) 
	
	LOCK = threading.Lock()
	
	try:
		while 1:
			
			global media1
			global numwlan1
			global soma1
			global media2
			global numwlan2
			global soma2
			
			proc = subprocess.Popen(["cat", "/proc/net/wireless"],stdout=subprocess.PIPE, universal_newlines=True)
			out, err = proc.communicate()	
			
			wlan1_rssi, wlan2_rssi = library2.parseRssi(out)
	 
		
			if(numwlan1 != 1):
				if ((abs(int(wlan1_rssi))) > abs(media1)*1.7):
					print " "
				else:
					buffwlan1.append(int(wlan1_rssi))
					calcMediaOfSignal1(abs(int(wlan1_rssi)))
					numwlan1 = numwlan1+1
					soma1=soma1+abs(int(wlan1_rssi))
			else:
				buffwlan1.append(int(wlan1_rssi))
				calcMediaOfSignal1(abs(int(wlan1_rssi)))
				numwlan1 = numwlan1+1
				soma1=soma1+abs(int(wlan1_rssi))
				
					
			if(numwlan2 != 1):
				if ((abs(int(wlan2_rssi))) > abs(media2)*1.7):
					print " "
				else:
					buffwlan2.append(int(wlan2_rssi))
					calcMediaOfSignal2(abs(int(wlan2_rssi)))
					numwlan2 = numwlan2+1
					soma2=soma2+abs(int(wlan1_rssi))
			else:
				buffwlan2.append(int(wlan2_rssi))
				calcMediaOfSignal2(abs(int(wlan2_rssi)))
				numwlan2 = numwlan2+1
				soma2=soma2+abs(int(wlan2_rssi))
			
			
			
			mAvg_wlan1 = library2.running_mean(buffwlan1.get(),KERNEL_SIZE)
			mAvg_wlan2 = library2.running_mean(buffwlan2.get(),KERNEL_SIZE)

			distance1 = library2.calculate_distance(mAvg_wlan1)
			distance2 = library2.calculate_distance(mAvg_wlan2)
			
			if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
				print "WLAN1: " + str(mAvg_wlan1.item())
				print "WLAN2: " + str(mAvg_wlan2.item())
				print "Distance 1: " + str(disance1)
				print "Distance 2: " + str(disance2)
				print ""
				
			
			absDiff = abs(abs(mAvg_wlan1) - abs(mAvg_wlan2))
			sgnDiff = abs(mAvg_wlan1) - abs(mAvg_wlan2)
						
			
			print "absDiff: " + str(absDiff)
			print "sgnDiff: " + str(sgnDiff)
			print ""
			

			if absDiff > 2:							
				if sgnDiff < -2:
					with LOCK:
						ser.write(RIGHT)
						print "RIGHT"				
				elif sgnDiff > 2:
					with LOCK:
						ser.write(LEFT)
						print "LEFT"
			else:
				with LOCK:
					ser.write(FORWARD)
					print "FORWARD"	
			
			
			if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):	
				time.sleep(0.01)
					
			
	except KeyboardInterrupt:
		sys.exit()
		ser.close()  

if __name__ == '__main__':
	main()

