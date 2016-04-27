import connector
import urllib2
import time
import threading
import Queue
from lxml import html

conn = connector.Connector()

def crawlProxies(address):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    try:
        proxyList = opener.open(address)
        print("Opened " + address)
    except:
        print('Failed to open URL, exiting...')
        exit()
    plain_html = proxyList.read()
    tree = html.fromstring(plain_html)
    hosts = tree.xpath('//td[1]/text()')
    ports = tree.xpath('//td[2]/text()')
    values = zip(hosts,ports)
    for h, p in values:
        try:
            conn.add_proxy(h,p)
        except:
            continue

crawlProxies("http://www.us-proxy.org/")
crawlProxies("http://www.sslproxies.org/")
crawlProxies("http://free-proxy-list.net/uk-proxy.html")

f=0
s=0
t=0

def validateProxy(key,tConn):
    global f,s,t    
    addr = "http://" + key['host'] + ":" + str(key['port'])
    proxy =  urllib2.ProxyHandler({'http': addr})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    try:
        a = urllib2.urlopen("http://panoramafirm.pl/",timeout=5)
        start = time.time()	
        if a.getcode()==200:
            print "GIT!"
            page = a.read()
            ping=(time.time()-start)*1000
            tConn.update_status(str(key['id']),1)
            tConn.update_timeout(str(key['id']),str(ping))
            s+=1       	
        else:
            tConn.update_status(str(key['id']),2)
            f+=1            
    except:
        t+=1
        tConn.update_status(str(key['id']),2)        

try:    
    proxies = conn.get_proxies_to_work()
    print("Got proxies to work")
except:
    print("There is no proxy with proper status")
    exit()

class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        tConn = connector.Connector()
        validateProxy(key,tConn)
        threads.remove(self)

threads=[]

i = 0
for key in proxies:
    i+=1
    if (i % 50 == 0):
        print "Done " + i + " proxies"
    while (len(threads) > 9):    
        try:
            myThread.sleep(1000)
        except:
            pass
    thread = myThread()
    threads.append(thread)
    thread.start()

print "Passed - ",s
print "Failed - ",f
print "Timeout error - ",t
