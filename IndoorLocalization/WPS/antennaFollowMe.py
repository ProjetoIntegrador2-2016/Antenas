import numpy as np
import sys
import subprocess
from struct import *
import serial
import time
import atexit
import threading
import library2
import definitions


class RingBuffer:
    """ class that implements a not-yet-full buffer """

    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """

        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur + 1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:] + self.data[:self.cur]

    def append(self, x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data


def main():

	ser = serial.Serial('/dev/ttyAMA0', 19200, timeout=1)

	buffAbs = RingBuffer(definitions.KERNEL_SIZE)
	buffSgn = RingBuffer(definitions.KERNEL_SIZE)
	buffwlan1 = RingBuffer(definitions.KERNEL_SIZE)
	buffwlan2 = RingBuffer(definitions.KERNEL_SIZE)

	LOCK = threading.Lock()

	try:
		while 1:
			proc = subprocess.Popen(["cat", "/proc/net/wireless"], stdout=subprocess.PIPE, universal_newlines=True)
			out, err = proc.communicate()
			
			wlan1_rssi, wlan2_rssi = library2.parseRssi(out)
			
			if definitions.numwlan1 != 1.0:
				if (abs(float(wlan1_rssi))) > abs(definitions.media1) * 1.7:
					print "SAMPLE DISREGARDED WLAN1"
				else:
					buffwlan1.append(float(wlan1_rssi))
					library2.calcMediaofSignal1(abs(float(wlan1_rssi)))
					definitions.numwlan1 = definitions.numwlan1 + 1
					definitions.soma1 = definitions.soma1 + abs(float(wlan1_rssi))
			else:
				buffwlan1.append(float(wlan1_rssi))
				library2.calcMediaofSignal1(abs(float(wlan1_rssi)))
				definitions.numwlan1 = definitions.numwlan1 + 1
				definitions.soma1 = definitions.soma1 + abs(float(wlan1_rssi))
		
			if definitions.numwlan2 != 1.0:
				if (abs(float(wlan2_rssi))) > abs(definitions.media2)*1.7:
					print "SAMPLE DISREGARDED WLAN2"
				else:
					buffwlan2.append(float(wlan2_rssi))
					library2.calcMediaofSignal2(abs(float(wlan2_rssi)))
					definitions.numwlan2 = definitions.numwlan2+1
					definitions.soma2 = definitions.soma2+abs(float(wlan1_rssi))
			else:
				buffwlan2.append(float(wlan2_rssi))
				library2.calcMediaofSignal2(abs(float(wlan2_rssi)))
				definitions.numwlan2 = definitions.numwlan2+1
				definitions.soma2 = definitions.soma2+abs(float(wlan2_rssi))

			if (definitions.numwlan1 > 50.0) & (definitions.numwlan2 > 50.0):
				library2.resetMediaofSignal1()
				library2.resetMediaofSignal2()			
			
			mAvg_wlan1 = library2.running_mean(buffwlan1.get(),definitions.KERNEL_SIZE)
			mAvg_wlan2 = library2.running_mean(buffwlan2.get(),definitions.KERNEL_SIZE)

			distance1 = library2.calculate_distance(mAvg_wlan1)
			distance2 = library2.calculate_distance(mAvg_wlan2)
			
			# if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
			# 	print "WLAN1: " + str(mAvg_wlan1.item())
			# 	print "WLAN2: " + str(mAvg_wlan2.item())
			# 	print "Distance 1: " + str(distance1)
			# 	print "Distance 2: " + str(distance2)
			# 	print ""
				
			
			absDiff = abs(abs(mAvg_wlan1) - abs(mAvg_wlan2))
			sgnDiff = abs(mAvg_wlan1) - abs(mAvg_wlan2)
						
			# print "absDiff: " + str(absDiff)
			# print "sgnDiff: " + str(sgnDiff)
			# print ""

			if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
				print "Potencia wlan1: " + str(mAvg_wlan1.item())
				d11 = library2.calculate_distance(float(mAvg_wlan1.item()))
				print "WLAN1 distance d1: " + str(d11)
				print ""
				print "Potencia wlan2: " + str(mAvg_wlan2.item())
				d22 = library2.calculate_distance(float(mAvg_wlan2.item()))
				print "WLAN2 distance d2: " + str(d22)
				print ""
				y_theta, y_alpha = library2.calcCoordY(d11,d22)
				print "Coordenada y_theta = " + str(y_theta) + ", Coordenada y_alpha = " + str(y_alpha)
				print ""
				#xPos = library2.calcCoordXPos(d11,d22)
				#print "X_pos = " + str(xPos)
				#print ""
				#xNeg= library2.calcCoordXNeg(d11,d22)
				#print "X_Neg = " + str(xNeg)
				#print ""
			
			#d11 = library2.calculate_distance(float(mAvg_wlan1.item()))
			#d22 = library2.calculate_distance(float(mAvg_wlan2.item()))
			#yPos1,yPos2 = library2.calcCoordY(d11,d22)			

			if absDiff > 2:							
				if sgnDiff < -2:
					with LOCK:
						#ser.write(definitions.RIGHT)
						print "Direction: RIGHT"
						xPos = library2.calcCoordXPos(d11,d22)
						print "Coordenada X_pos= " + str(xPos)
						print ""
						if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
							msg = (" %.2f, %.2f" % (xPos, y_theta))
							print msg
							print "------------------"
							ser.write(msg.encode('ascii'))				
				elif sgnDiff > 2:
					with LOCK:
						#ser.write(definitions.LEFT)
						print "Direction: LEFT"
						xNeg= library2.calcCoordXNeg(d11,d22)
						print "Coordenada X_Neg = " + str(xNeg)
						print ""
						if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
							msg = (" %.2f, %.2f" % (xNeg, y_theta))
							print msg
							print "------------------"
							ser.write(msg.encode('ascii'))	
			else:
				with LOCK:
					print "Direction: FORWARD"
					if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):
						msg = (" %.2f, %.2f" % (0, y_theta))
						print msg
						print "------------------"
						ser.write(msg.encode('ascii'))	
						
			
			
			if (mAvg_wlan1.size != 0) & (mAvg_wlan2.size != 0):	
				time.sleep(0.1)
					
			
	except KeyboardInterrupt:
		sys.exit()
		ser.close()  

if __name__ == '__main__':
	main()

