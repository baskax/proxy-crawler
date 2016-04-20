import connector
import urllib2
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
        print((h,p), " added to list")
    except:
        continue



