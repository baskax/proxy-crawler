import urllib2
import time
from sys import exit
import threading
import PySQLPool
from lxml import html

PySQLPool.getNewPool().maxActiveConnections = 12    #nothing to explain
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
            continue    #bad exception handling but works for duplicate entries (we use insert, not insert ignore)

#all these three sites looks the same inside so we can use one mechanism to crawl proxies
crawlProxies("http://www.us-proxy.org/")
crawlProxies("http://www.sslproxies.org/")
crawlProxies("http://free-proxy-list.net/uk-proxy.html")

#succeded, failed and timeouted counters
f=0
s=0
t=0

def validateProxy(key,tConn):
    global f,s,t    
    addr = "http://" + key['host'] + ":" + str(key['port'])     #concatenating proxy string
    proxy =  urllib2.ProxyHandler({'http': addr})
    id = key['id']
    opener = urllib2.build_opener(proxy)
    tConn.Query("select user_agent from proxy_ua order by rand() limit 1")      #random user-agent string from database
    user_agent = tConn.record
    opener.addheaders = [('User-agent', str(user_agent))]
    urllib2.install_opener(opener)
    try:
        a = urllib2.urlopen("http://panoramafirm.pl/",timeout=10)
        start = time.time()	
        if a.getcode()==200:            #when page gave us status 200
            page = a.read()             #we are reading the whole page (for benchmarking issues)
            ping=(time.time()-start)*1000   #used to measure time between beginning of the connection and final reading the whole page
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
    if proxies:
        print("Got proxies to work")
    else:
        print("There is no proxy with proper status, exiting...")
        sys.exit()
except:
    exit()

class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)     #inherited from superclass Thread
    def run(self):
        tConn = PySQLPool.getNewQuery(db)   #new Query object compatible with threading
        validateProxy(key,tConn)
        PySQLPool.commitPool()  #commiting current transcations
        PySQLPool.cleanupPool() #closing existing connections
        threads.remove(self)

threads=[]      #list of currently working threads

i = 0
for key in proxies:
    i+=1
    if (i % 50 == 0):
        print("Done " + str(i) + " proxies")
    while (len(threads) > 9):   #10 threads at once 
        try:
            myThread.sleep(1000)
        except:
            pass
    thread = myThread()
    threads.append(thread)      #appends current thread to threads list
    thread.start()      #starts current thread

print "Passed - ",s
print "Failed - ",f
print "Timeout error - ",t
