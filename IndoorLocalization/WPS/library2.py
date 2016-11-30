import numpy as np
import definitions
import math

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
	
        
def parseRssi(output):
	for line in output.split("\n"):
		line_wlan1 = match(line,definitions.ADPT1) #wlan1 4 ex
		line_wlan2 = match(line,definitions.ADPT2)
		if line_wlan1 != None:
			wlan1_Prssi = line_wlan1[line_wlan1.index('-'):find_2nd(line_wlan1,'.')]
		if line_wlan2 != None:
			wlan2_Prssi = line_wlan2[line_wlan2.index('-'):find_2nd(line_wlan2,'.')] 
            
	return wlan1_Prssi, wlan2_Prssi

def calculate_distance(mAvg_wlan):
	d0 = 100.0
	p0= -20.0 
	np = 2.0
	d = (d0 * 10.0**((p0 - mAvg_wlan)/(np*10.0)))
	return d 

def calcMediaofSignal1(wlan1):
	definitions.media1 = (wlan1+definitions.soma1)/definitions.numwlan1

def resetMediaofSignal1(): 
    definitions.media1 = 0.0
    definitions.numwlan1 = 1.0
    definitions.soma1 = 0.0 
        
def calcMediaofSignal2(wlan2):	
	definitions.media2 = (wlan2+definitions.soma2)/definitions.numwlan2

def resetMediaofSignal2():
    definitions.media2 = 0.0
    definitions.numwlan2 = 1.0
    definitions.soma2 = 0.0

# Do something to avg the values
def calcCoordY(d11, d22):
    variableForAcos = ((definitions.d1t**2)+(d22**2)-(d11**2))/(2*definitions.d1t*d22)
    #print "Variable Test = " + str(variableForAcos)
    if (variableForAcos > 1.0):
	variableForAcos = 1.0
    if (variableForAcos < -1.0):
	variableForAcos = -1.0
    theta_deg = math.degrees(math.acos(variableForAcos))
    theta_rad = math.radians(theta_deg)
    #print "theta_deg = " + str(theta_deg)
    variableForAcos2 = ((d11**2)+(definitions.d1t**2)-(d22**2))/(2*definitions.d1t*d11)
    if (variableForAcos2 > 1.0):
	variableForAcos2 = 1.0
    if (variableForAcos2 < -1.0):
	variableForAcos2= -1.0
    alpha_deg = math.degrees(math.acos(variableForAcos2))
    alpha_rad = math.radians(alpha_deg)
    #print "alpha_deg = " + str(alpha_deg)
    yTheta = d22*(math.sin(theta_rad))
    yAlpha = d11*(math.sin(alpha_rad))
    return yTheta, yAlpha

def calcCoordXPos(d11, d22):
    variableForAcos = ((d11**2)+(definitions.d1t**2)-(d22**2))/(2*definitions.d1t*d11)
    if (variableForAcos > 1.0):
	variableForAcos = 1.0
    if (variableForAcos < -1.0):
	variableForAcos= -1.0
    alpha_rad = math.acos(variableForAcos)
    xPos = math.cos(alpha_rad)*d11
    return xPos

#Abs value to be subtracted later
def calcCoordXNeg(d11, d22):
    variableForAcos = ((definitions.d1t**2)+(d22**2)-(d11**2))/(2*definitions.d1t*d22)
    if (variableForAcos > 1.0):
	variableForAcos = 1.0
    if (variableForAcos < -1.0):
	variableForAcos= -1.0
    theta_rad = math.acos(variableForAcos)
    xNeg = (math.cos(theta_rad))*d22
    return xNeg
