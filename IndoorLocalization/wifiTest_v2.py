# Get signal strength of usb wifi adapter 
# Adaptors connected to a wireless network

import sys
import subprocess

adpt1 = "wlan1"
adpt2 = "wlan2"

# Signal level is on same line as Quality data so a bit of ugly
# hacking needed...
#def get_signal_level(cell):   
    #return matching_line(cell,adpt1).split("Signal level=")[1]

#def matching_line(lines, keyword):
    #"""Returns the first matching line in a list of lines. See match()"""
    #for line in lines:
        #matching=match(line,keyword)
        #if matching!=None:
            #return matching
    #return None
    
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
        
    cells=[[]]

    proc = subprocess.Popen(["cat", "/proc/net/wireless"],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()
    
    for line in out.split("\n"):
        cell_line = match(line,adpt1) #wlan1 4 ex
        if cell_line != None:
            cells.append([])          
        cells[-1].append(line.rstrip())
    
    wlan1_rssi = cells[1][0]
    wlan2_rssi = cells[0][2]
    print "wlan1 rssi: " + wlan1_rssi[cells[1][0].index('-'):find_2nd(wlan1_rssi,'.')]
    print "wlan2 rssi: " + wlan2_rssi[cells[0][2].index('-'):find_2nd(wlan2_rssi,'.')]
    

    
    
    

    

if __name__ == '__main__':
	main()
