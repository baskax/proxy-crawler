import PySQLPool

class Connector:
    
    __db = PySQLPool.getNewConnection(host="127.0.0.1",port=3306,user="root",password="howtosaygoodbye'x",db="proxy")
    __query = PySQLPool.getNewQuery(__db)
    
    def get_proxy(self,id):
        self.__query.Query("select host,port,timeout from proxy_list where id='%s'" % id)
        return self.__query.record
    
    def get_proxies_to_work(self):
        self.__query.Query("select * from proxy_list where status = 0")
        return self.__query.record
        
    def get_all_proxies(self):
        self.__query.Query("select * from proxy_list")
        return self.__query.record
    
    def update_timeout(self,id,timeout):
        self.__query.Query("update proxy_list set timeout='%s' where id=%s", (timeout,id))        
    
    def update_status(self,id,status):
        self.__query.Query("update proxy_list set status='%s' where id=%s", (status,id))
        
    def add_proxy(self,host,port):
        self.__query.Query("insert into proxy_list (host,port) values ('%s','%s')", (host,port))
            
