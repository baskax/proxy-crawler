import urllib2
import time
import threading
import PySQLPool
from lxml import html

db = PySQLPool.getNewConnection(host="127.0.0.1",port=3306,user="root",password="howtosaygoodbye'x",db="proxy")
query = PySQLPool.getNewQuery(db)

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
    for host, port in values:
        try:
            query.Query("insert into proxy_list (host,port) values ('%s','%s')", (host,port))
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
    id = key['id']
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    try:
        a = urllib2.urlopen("http://panoramafirm.pl/",timeout=5)
        start = time.time()	
        if a.getcode()==200:            
            page = a.read()
            ping=(time.time()-start)*1000
            tConn.Query("update proxy_list set status='1' where id='{0}'".format(str(id)))
            tConn.Query("update proxy_list set timeout='{0}' where id={1}".format(str(ping),str(id)))
            s+=1       	
        else:
            tConn.Query("update proxy_list set status='2' where id='{0}'".format(str(id)))
            f+=1            
    except:
        t+=1
        tConn.Query("update proxy_list set status='2' where id='{0}'".format(str(id)))         

try:    
    query.Query("select * from proxy_list where status = 0")
    proxies = query.record
    print("Got proxies to work")
except:
    print("There is no proxy with proper status")
    exit()

class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        tConn = PySQLPool.getNewQuery(db)
        validateProxy(key,tConn)
        PySQLPool.commitPool()
        PySQLPool.cleanupPool()
        threads.remove(self)

threads=[]

i = 0
for key in proxies:
    i+=1
    if (i % 50 == 0):
        print("Done " + str(i) + " proxies")
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
