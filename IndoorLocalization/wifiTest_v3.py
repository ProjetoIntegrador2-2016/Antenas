# Get signal strength of usb wifi adapter 
# Adaptors connected to a wireless network

import sys
import subprocess
from struct import *
import binascii

adpt1 = "wlan1"
adpt2 = "wlan2"
    
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

def main():    

    proc = subprocess.Popen(["cat", "/proc/net/wireless"],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()
    
    for line in out.split("\n"):
        line_wlan1 = match(line,adpt1) #wlan1 4 ex
        line_wlan2 = match(line,adpt2)
        if line_wlan1 != None:
            wlan1_rssi = line_wlan1[line_wlan1.index('-'):find_2nd(line_wlan1,'.')]
        if line_wlan2 != None:
            wlan2_rssi = line_wlan2[line_wlan2.index('-'):find_2nd(line_wlan2,'.')]          
   
    print "wlan1 rssi: " + wlan1_rssi
    print "wlan2_rssi: " + wlan2_rssi
    print ""
    
    right = pack('B',0)
    left = pack('B',1)
    forward = pack('B',2)
    backward = pack('B',255)
    
    print "Byte code for right direction: " +  binascii.hexlify(right) 
    print "Byte code for left direction: " + binascii.hexlify(left)
    print "Byte code for forward direction: " + binascii.hexlify(forward)
    print "Byte code for backward direction: " + binascii.hexlify(backward)
    print ""
    

if __name__ == '__main__':
	main()
