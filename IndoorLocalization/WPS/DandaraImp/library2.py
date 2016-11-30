

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
		line_wlan1 = match(line,ADPT1) #wlan1 4 ex
		line_wlan2 = match(line,ADPT2)
		if line_wlan1 != None:
			wlan1_Prssi = line_wlan1[line_wlan1.index('-'):find_2nd(line_wlan1,'.')]
		if line_wlan2 != None:
			wlan2_Prssi = line_wlan2[line_wlan2.index('-'):find_2nd(line_wlan2,'.')] 
            
	return wlan1_Prssi, wlan2_Prssi

def calculate_distance(mAvg_wlan):
	d0 = 100
	p0= -20 
	np = 2
	d = (d0 * 10**((p0 - mAvg_wlan)/(np*10)))

	return d 

	
