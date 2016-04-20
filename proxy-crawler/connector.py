import MySQLdb

class Connector:
    
    __db = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="",db="proxy")
    __cur = __db.cursor()
    
    def get_proxy(self,id):
        self.__cur.execute("select host,port,timeout from proxy_list where id=%s" % id)
        return self.__cur.fetchall()
    
    def get_all_proxies(self):
        self.__cur.execute("select * from proxy_list")
        return self.__cur.fetchall()
    
    def update_timeout(self,id,timeout):
        self.__cur.execute("update proxy_list set timeout='%s' where id=%s;", (timeout,id))
        self.__db.commit()        
    
    def update_status(self,id,status):
        self.__cur.execute("update proxy_list set status='%s' where id=%s;", (status,id))
        self.__db.commit()
        
    def add_proxy(self,host,port):
        self.__cur.execute("insert into proxy_list (host,port) values (%s,%s)", (host,port))
        self.__db.commit()
