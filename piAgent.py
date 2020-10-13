from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import check_output
import socket
import traceback
import time

lastRssi=None
lastUpdatesTime=0
lastUpdates=None

def getRssi():
	global lastRssi
	out = check_output(["/sbin/iwconfig","wlan0"]).decode("ASCII")
	j=out.index("Signal level=")+13;
	k=out.index("/",j);
	rssi=float(out[ j : k ]);
	if lastRssi==None:
		lastRssi=rssi
	else:
		lastRssi=lastRssi*0.9+rssi*0.1
	return int(lastRssi)
	
def getDiskAvailable():
	out = check_output(["df"]).decode("ASCII")
	lines = out.splitlines()
	result=None
	for line in lines:
		parts=line.split();
		if parts[0]=="/dev/root":
			result=float(parts[3])/(1000)
			break
	return result
		
def getLoadAverage():
	out = check_output(["cat","/proc/loadavg"]).decode("ASCII")
	parts=out.split();
	return float(parts[1])
	
def getCPUTemp():
	line = check_output(["/usr/bin/vcgencmd","measure_temp"]).decode("ASCII")
	temp=line[ line.index("temp=")+5 : line.index("'C") ]
	return float(temp)
	
def getHostname():
	return socket.gethostname()
	
def getUptime():
	out = check_output(["cat","/proc/uptime"]).decode("ASCII")
	parts=out.split();
	return float(parts[0])/3600
	
def getFreeMemory():
	out = check_output(["cat","/proc/meminfo"]).decode("ASCII")
	lines = out.splitlines()
	parts=lines[2].split();
	return int(parts[1])/1000

def getUpdates():
	global lastUpdatesTime, lastUpdates
	t=time.time()
	if (t-lastUpdatesTime>86400):
		#print {'running updates'}
		line = check_output(["bash","-c","/usr/bin/aptitude search ~U | wc -l"]).decode("ASCII")
		lastUpdates=int(line)
		lastUpdatesTime=t
	return lastUpdates
	
def getOS():
	out = check_output(["cat","/etc/os-release"]).decode("ASCII")
	lines = out.splitlines()
	result=None
	for line in lines:
		if line.startswith('PRETTY_NAME'):
			result=line[ line.index("=")+2 : line.rindex("\"") ]
			break;
	return result;
	
def onAgent():
	try:
		hostname=getHostname();
		rssi=getRssi();
		diskAvailable=getDiskAvailable()
		loadAverage=getLoadAverage();
		cpuTemp=getCPUTemp()
		uptime=getUptime()
		freeMem=getFreeMemory()
		updates=getUpdates()
		os=getOS()
		
		return "<agent hostname='{}' rssi='{:.0f}' diskAvailableMb='{:.0f}' freeMemMb='{:.0f}' loadAverage='{:.2f}' cpuTempC='{:.1f}' uptimeHours='{:.0f}' updatesAvailable='{:.0f}' os='{}'/>".format(
			hostname,rssi,diskAvailable,freeMem, loadAverage,cpuTemp,uptime,updates,os)
	except Exception as e:
		tb = traceback.format_exc()
		print(str(e))
		return tb
		#return str(e)
	
class S(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
    	if self.path=="/agent":
    		data=onAgent()
    	else:
    		data="<div>404</div>"
    	self.send_response(200)
    	self.send_header('Content-type',"text/xml")
    	self.end_headers()
    	self.wfile.write(data.encode('utf-8'))
    	return

    def do_HEAD(self):
        self._set_headers()

def run(server_class=HTTPServer, handler_class=S, port=8099):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
