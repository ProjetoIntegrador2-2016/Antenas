# University of Brasilia - Campus Gama (FGA)
# Smart Cart Project

	# Get signal strength of usb wifi adapter 
	# Adapters connected to a wireless network hosted in other pi
import numpy as np
#import scipy as sp
import sys
import subprocess
from struct import *
import serial
import time
import atexit
import threading

# Definitions
ADPT1 = "wlan1" #right
ADPT2 = "wlan2" #left
MAX = 4 # Maximum affordable difference between readings for forward case 
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
        
#---------------------------------------------------------------------------------#
    
def find_2nd(string, substring):
	return string.find(substring, string.find(substring) + 1)
	
		
def match(line,keyword):
    """If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise returns None"""
    line=line.lstrip()
    length=len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None
        
def running_mean(x, N):
	cumsum = np.cumsum(np.insert(x, 0, 0)) 
	actMean = (cumsum[N:] - cumsum[:-N]) / N  
	return actMean
	
#def runningMeanFast(x, N):
	#return np.convolve(x, np.ones((N,))/N)[(N-1):]
        
#def kill_subprocesses():
	#for proc in procs:
		#proc.kill()
        
def parseRssi(output):
	for line in output.split("\n"):
		line_wlan1 = match(line,ADPT1) #wlan1 4 ex
		line_wlan2 = match(line,ADPT2)
		#wlan1_Prssi = 0
		#wlan2_Prssi = 0
		if line_wlan1 != None:
			wlan1_Prssi = line_wlan1[line_wlan1.index('-'):find_2nd(line_wlan1,'.')]
		if line_wlan2 != None:
			wlan2_Prssi = line_wlan2[line_wlan2.index('-'):find_2nd(line_wlan2,'.')] 
            
	return wlan1_Prssi, wlan2_Prssi
	
def calcMedia1(wlan1):
	global media1
	global numwlan1
	global soma1 
	media1 = (wlan1+soma1)/numwlan1
	
	
def calcMedia2(wlan2):	
	global media2
	global numwlan2
	global soma2
	media2 = (wlan2+soma2)/numwlan2

def main():    
	# Instantiate and configure serial port object
	ser = serial.Serial('/dev/ttyAMA0', 19200, timeout=1)
    #ser.open() # serial is already open
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
			
			wlan1_rssi, wlan2_rssi = parseRssi(out)
	 
			#response = ser.readline()
			#print response
			
			# DEBUG
			#print "wlan1 rssi: " + wlan1_rssi
			#print "wlan2 rssi: " + wlan2_rssi
			#print ""  
			
			#buffwlan1.append(int(wlan1_rssi))
			#buffwlan2.append(int(wlan2_rssi))		

			#print media1
			#print media2
		
			if(numwlan1 != 1):
				if ((abs(int(wlan1_rssi))) > abs(media1)*1.7):
					print "oi1"
				else:
					buffwlan1.append(int(wlan1_rssi))
					#print buffwlan1.get()
					calcMedia1(abs(int(wlan1_rssi)))
					numwlan1 = numwlan1+1
					soma1=soma1+abs(int(wlan1_rssi))
			else:
				buffwlan1.append(int(wlan1_rssi))
				calcMedia1(abs(int(wlan1_rssi)))
				numwlan1 = numwlan1+1
				soma1=soma1+abs(int(wlan1_rssi))
				
					
			if(numwlan2 != 1):
				if ((abs(int(wlan2_rssi))) > abs(media2)*1.7):
					print "oi2"
				else:
					buffwlan2.append(int(wlan2_rssi))
					#print buffwlan2.get()
					calcMedia2(abs(int(wlan2_rssi)))
					numwlan2 = numwlan2+1
					soma2=soma2+abs(int(wlan1_rssi))
			else:
				buffwlan2.append(int(wlan2_rssi))
				calcMedia2(abs(int(wlan2_rssi)))
				numwlan2 = numwlan2+1
				soma2=soma2+abs(int(wlan2_rssi))
			
			
			#print buffwlan1.get()
			#print buffwlan2.get()
			
			mAvg_wlan1 = running_mean(buffwlan1.get(),KERNEL_SIZE)
			mAvg_wlan2 = running_mean(buffwlan2.get(),KERNEL_SIZE)
			
			if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
				print "WLAN1: " + str(mAvg_wlan1.item())
				print "WLAN2: " + str(mAvg_wlan2.item())
				print ""
				
			#absDiff = abs(abs(int(wlan1_rssi)) - abs(int(wlan2_rssi)))
			#sgnDiff = abs(int(wlan1_rssi)) - abs(int(wlan2_rssi))
			
			absDiff = abs(abs(mAvg_wlan1) - abs(mAvg_wlan2))
			sgnDiff = abs(mAvg_wlan1) - abs(mAvg_wlan2)
			
			#buffAbs.append(int(absDiff))
			#buffSgn.append(int(sgnDiff))
			#print buff.get()
			#rmRes = running_mean(buffAbs.get(),KERNEL_SIZE)
			#print rmRes
			
			# DEBUG
			#print "Absolute signal strength difference between wlan1 and wlan2: " + str(absDiff)
			#print ""			
			
			#print "absDiff: " + str(absDiff)
			#print "sgnDiff: " + str(sgnDiff)
			print ""
			
			#print "NUMLAN1: " + str(numwlan1)		
			#print "NUMLAN2: " + str(numwlan2)
			#print ""
			
			if absDiff > 2:							
				if sgnDiff < -2:
					with LOCK:
						ser.write(RIGHT)
						#print "RIGHT"				
				elif sgnDiff > 2:
					with LOCK:
						ser.write(LEFT)
						#print "LEFT"
			else:
				with LOCK:
					ser.write(FORWARD)
					#print "FORWARD"	
			
			
			
				#ser.write(RIGHT)
			
			
			if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):	
				time.sleep(0.1)
					
			
	except KeyboardInterrupt:
		sys.exit()
		ser.close()  

if __name__ == '__main__':
	main()

