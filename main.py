import connector
import urllib2
import time
from lxml import html

def showIntro():
    print('#####################################')
    print('## P R O X Y L I S T C R A W L E R ##')
    print('#####################################')


showIntro()
conn = connector.Connector()
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
try:
    proxyList = opener.open("http://www.sslproxies.org/")
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
print("Got proxies, checking.")
proxies = conn.get_proxies_to_work()
f=0
s=0
t=0
for key in proxies:
    addr = "https://" + key[1] + ":" + str(key[2])
    proxy =  urllib2.ProxyHandler({'https': addr})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    try:
	a = urllib2.urlopen("https://prod.ceidg.gov.pl/CEIDG/CEIDG.Public.UI/Search.aspx",timeout=5)
        start = time.time()	
    	if a.getcode()==200:
	    page = a.read()
            ping=(time.time()-start)*1000
	    conn.update_status(str(key[0]),1)
	    conn.update_timeout(str(key[0]),ping)
	    s+=1       	
        else:        
            conn.update_status(str(key[0]),2)
    	    f+=1
	    continue
    except:
	t+=1
	conn.update_status(str(key[0]),2)	
	continue	
print "Passed - ",s
print "Failed - ",f
print "Timeout error - ",t
