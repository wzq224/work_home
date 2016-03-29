# coding:utf-8 # 
import requests
import re
import json
from bs4 import BeautifulSoup
import MySQLdb
import threading  
import time 

XSRF = ""
conn = None
#cursor="" 
HEADERS_BASE = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36', 
        'Referer': 'http://www.zhihu.com/'
    }

def get_xsrf(url=None):
    r = requests.get(url, headers=HEADERS_BASE)        
    xsrf = re.search(r'(?<=name="_xsrf" value=")[^"]*(?="/>)', r.text)
    if xsrf == None:
        return ''
    else:
        return xsrf.group(0)


# 模拟登录 返回cookie
def get_login_cookie():
    url = 'http://www.zhihu.com'
    login_url = url+'/login/email'
    login_data = {
        'email': 'wzq.ok@foxmail.com', 
        'password': 'zhiqian123',
        'rememberme': 'true',
    }
    
    XSRF = get_xsrf(url)
    print "xsrf:",XSRF
    login_data['_xsrf'] = XSRF.encode('utf-8')
    
    # captcha_url = 'http://www.zhihu.com/captcha.gif'
    # captcha = s.get(captcha_url, stream=True)
    # print captcha
    # f = open('captcha.gif', 'wb')
    # for line in captcha.iter_content(10):
    #     f.write(line)
    # f.close()
   
    #print u'输入验证码:' 
    #captcha_str = raw_input() 
    #login_data['captcha'] = captcha_str

    res = requests.post(login_url, headers=HEADERS_BASE, data=login_data)
    print "status_code:",res.status_code

    m_cookies = res.cookies

    return m_cookies



# 获取粉丝
def get_next_followers(hash_id="",offset=0,cookies=None,num=0):
    next_followers_url = "https://www.zhihu.com/node/ProfileFollowersListV2"
    return get_next_users(hash_id,offset,cookies,next_followers_url,num)

# 获取关注的人
def get_next_followees(hash_id="",offset=0,cookies=None):
    next_followees_url = "https://www.zhihu.com/node/ProfileFolloweesListV2"
    return get_next_users(hash_id,offset,cookies,next_followees_url)

def get_next_users(hash_id="",offset=0,cookies=None,next_url="",num=0):
    params = dict()
    params["offset"] = offset
    params["order_by"] = "created"
    params["hash_id"] = hash_id

    next_data = dict()
    next_data["params"] = json.JSONEncoder().encode(params)
    next_data["_xsrf"] = XSRF
    try:
        res = requests.get(next_url, headers=HEADERS_BASE, cookies=cookies, data=next_data, timeout=1)
        print "status_code:",res.status_code,"offset:",offset,"hash_id:",hash_id
        return res.content
    except Exception, e:
        #raise e
        print "ERROR"
    return ""
    



def findall_hash_id():
    m_cookies = get_login_cookie()
    hash_id = "551a35ab184779ae3110b56aa252d6b7"

    hash_id_pattern = re.compile(r'data-id="[0-9a-z]*"')
    hash_id_pattern2 = re.compile(r'[0-9a-z]{32}')

    for x in range(0,1):
        offset = x*20
        #print offset
        html = get_next_followers("551a35ab184779ae3110b56aa252d6b7",offset,m_cookies)
        if html == "":
            continue

        users_hash_id = hash_id_pattern.findall(html)
        
        for temp_hash_id in users_hash_id:
            s = hash_id_pattern2.search(temp_hash_id).group()
            print s


    

def get_follwes_profile(m_cookies,hash_id,page_num,conn,offset=0,num=0):

    
    users_model_pattern = re.compile(r'<div class="zm-profile-card zm-profile-section-item zg-clear no-hovercard">',re.M)
    hash_id_pattern = re.compile(r'data-id="[0-9a-z]{32}"')
    user_name_pattern = re.compile(r'title="[\s\S]*?"')
    user_desc_pattern = re.compile(r'<div class="zg-big-gray">[\s\S]*?</div>')
    proflie_url_pattern = re.compile(r'href="[/a-zA-Z0-9-_\.]*?">')
    followers_pattern = re.compile(r'\d+ 关注者')
    asks_pattern = re.compile(r'\d+ 提问')
    answers_pattern = re.compile(r'\d+ 回答')
    zans_pattern = re.compile(r'\d+ 赞同')
    #users = []
    start = offset/20
    for x in range(start,page_num+1):
        offset = x*20
        #print offset
        html = get_next_followers(hash_id,offset,m_cookies,num)
        users_models = users_model_pattern.split(html)

        for users_model in users_models:
            user = dict()
            #print users_model
            temp_hash_id = hash_id_pattern.search(users_model)
            if temp_hash_id != None:
                user["hash_id"] = temp_hash_id.group().replace("data-id=\"","").replace("\"","")
                
                user_name = user_name_pattern.search(users_model)
                if user_name != None:
                    user["user_name"] = user_name.group().replace("title=","").replace("\"","")
                else:
                    user["user_name"] = ""

                user_desc = user_desc_pattern.search(users_model)
                if user_desc != None:
                    user["user_desc"] = user_desc.group().replace("<div class=\"zg-big-gray\">","").replace("</div>","").replace("\\","\\\\")
                else:
                    user["user_desc"] = ""

                proflie_url = proflie_url_pattern.search(users_model)
                if proflie_url != None:
                    user["proflie_url"] = proflie_url.group().replace("href=\"","").replace("\">","")
                else:
                    user["proflie_url"] = ""

                followers = followers_pattern.search(users_model)
                if followers != None:
                    user["followers"] = (followers.group().replace(" 关注者",""))
                else:
                    user["followers"] = 0

                asks = asks_pattern.search(users_model)
                if asks != None:
                    user["asks"] = (asks.group().replace(" 提问",""))
                else:
                    user["asks"] = 0
                    
                  
                answers = answers_pattern.search(users_model)
                if answers != None:
                    user["answers"] = (answers.group().replace(" 回答",""))
                else:
                    user["answers"] = 0

                zans = zans_pattern.search(users_model)
                if zans != None:
                    user["zans"] = (zans.group().replace(" 赞同",""))
                else:
                    user["zans"] = 0

                #insert_user_profile(conn,user)
                #users.append(user)
                #for user in users:
                if check_hash_id(conn,user["hash_id"]):
                    continue
                else:
                    insert_user_profile(conn,user)
                    add_queue(conn,user["hash_id"])
            
                if check_relation(conn,hash_id,user["hash_id"]):
                    continue
                else:
                    add_relation(conn,hash_id,user["hash_id"])

    #return users


#def work():

    




def check_relation(conn,user_hash_id,follower_hash_id):
    check_sql = "select 1 from user_followers_relations_%s where user_hash_id='%s' AND follower_hash_id='%s'"%(hash_id_to_num(user_hash_id),user_hash_id,follower_hash_id)
    #print check_sql
    cursor = conn.cursor()
    n = 0
    try:
        cursor.execute(check_sql)
        n = len(cursor.fetchall())
 
    except Exception, e:
        raise e
    finally:
        return n>0

def check_hash_id(conn,hash_id):
    check_sql = "select 1 from user_profile_%s where hash_id='%s'"%(hash_id_to_num(hash_id),hash_id)

    cursor = conn.cursor()
    n = 0
    try:
        cursor.execute(check_sql)
        n = len(cursor.fetchall())
    except Exception, e:
        raise e
    finally:
        return n>0


def get_new_user_id(conn):
    sql = "select min(id) from user_queue where flag=0"
    cursor = conn.cursor()
    cursor.execute(sql)
    user_info = cursor.fetchall()
    user = dict()
    if len(user_info) >= 1:
        if len(user_info[0]) >= 1:
            _id = int(user_info[0][0])
            update_sql = "update user_queue set flag=1 where id=%d" % _id
            cursor.execute(update_sql)
            conn.commit()
            return _id
    return 0


def get_user_info(conn,hash_id):
    sql = "select id,hash_id,followers from user_profile_%s where hash_id='%s'" %(hash_id_to_num(hash_id),hash_id)
    #print sql
    cursor = conn.cursor()
    cursor.execute(sql)
    user_info = cursor.fetchall()

    user = dict()
    if len(user_info) >= 1:
        if len(user_info[0]) >= 1:
            user["id"] = int(user_info[0][0])
            user["hash_id"] = str(user_info[0][1])
            user["followers"] = int(user_info[0][2])
    return user

def get_max_id(conn):
    sql = "select max(id) from user_queue"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    _id = 0
    if len(result) >= 1:
        if len(result[0]) >= 1:
            _id = int(result[0][0])
    return _id

def get_hash_id(conn,_id):
    sql = "select hash_id from user_queue where id=%d" % _id
    #update_sql = "update user_queue set flag=1 where id=%d" % _id
    #print sql
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    hash_id = ""
    if len(result) >= 1:
        if len(result[0]) >= 1:
            hash_id = str(result[0][0])
    #cursor.execute(update_sql)
    #conn.commit()
    return hash_id

def add_queue(conn,hash_id):
    sql = "insert into user_queue(hash_id,flag) value (\"%s\",0)" % hash_id
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

def add_relation(conn,user_hash_id,follower_hash_id):
    relation_sql = ""
    cursor = conn.cursor()
    try:
        relation_sql = "insert into user_followers_relations_%s(user_hash_id,follower_hash_id) value(\"%s\",\"%s\")"%(hash_id_to_num(user_hash_id),user_hash_id,follower_hash_id)

    except Exception, e:
        raise e
    #print relation_sql
    cursor.execute(relation_sql)
    conn.commit()


def insert_user_profile(conn,user):
    insert_user_sql=""
    cursor = conn.cursor()
    try:
        insert_user_sql = "insert into user_profile_%s(hash_id,user_name,user_desc,proflie_url,followers,asks,answers,zans) value(\"%s\",\"%s\",\"%s\",\"%s\",%s,%s,%s,%s)"%(hash_id_to_num(user["hash_id"]),user["hash_id"],user["user_name"],user["user_desc"],user["proflie_url"],user["followers"],user["asks"],user["answers"],user["zans"])
    except Exception, e:
        raise e
    #print insert_user_sql
    cursor.execute(insert_user_sql)
    conn.commit()




def find_user(m_cookies,conn,num):
 
    offset = 0
    i = get_new_user_id(conn)
    if i == 0:
        print "get min id error"
        return

    while i <= get_max_id(conn):
        _id = i
        
        print "thread num:",num,"id:",_id

        hash_id = get_hash_id(conn,_id)
        
        if hash_id == "":
            continue
        new_user = get_user_info(conn,hash_id)
        if len(new_user) == 0:
            continue
        
    
        host_hash_id = new_user["hash_id"]
        page_num = int(int(new_user["followers"])/20)

        users = get_follwes_profile(m_cookies,host_hash_id,page_num,conn,offset,num)
        i = get_new_user_id(conn)
        if i == 0:
            print "get min id error"
            break




def hash_id_to_num(hash_id):
    
    i = 0
    for x in xrange(0,len(hash_id)):
        i = i+ord(hash_id[x])
    return "%03d" % (i%1000)

def create_tables():
    conn=MySQLdb.connect(host="127.0.0.1",user="spider",passwd="spider123",db="zhihu_spider",charset="utf8")
    cursor = conn.cursor()
    create_table_sql = """
CREATE TABLE IF NOT EXISTS `user_profile_%03d` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hash_id` varchar(32) CHARACTER SET latin1 DEFAULT NULL,
  `user_name` varchar(32) DEFAULT NULL,
  `user_desc` varchar(256) DEFAULT NULL,
  `proflie_url` varchar(128) CHARACTER SET latin1 DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `asks` int(11) DEFAULT NULL,
  `answers` int(11) DEFAULT NULL,
  `zans` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hash_id` (`hash_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1684 DEFAULT CHARSET=utf8;
    """

    for x in xrange(0,1000):
        cursor.execute(create_table_sql % x)
        conn.commit()

    
    

def mysql_test():
    conn=MySQLdb.connect(host="127.0.0.1",user="spider",passwd="spider123",db="zhihu_spider",charset="utf8")
    print get_hash_id(conn,1)
    add_queue(conn,"69865e1245455c3bd3f0eeacdad64c5b") 



class MySpiderThread(threading.Thread): #The timer class is derived from the class threading.Thread  
    def __init__(self, num, conn,m_cookies):  
        threading.Thread.__init__(self)  
        self.thread_num = num   
        self.thread_stop = False
        self.conn = conn   
        self.m_cookies = m_cookies
    def run(self): #Overwrite run() method, put what you want the thread do here
        print self.m_cookies,self.conn,self.thread_num
        #find_user(self.m_cookies,self.conn,self.thread_num)
    
    def stop(self):  
        self.thread_stop = True 



def main():
    conn=MySQLdb.connect(host="127.0.0.1",user="spider",passwd="spider123",db="zhihu_spider",charset="utf8")


    m_cookies = get_login_cookie()
    find_user(m_cookies,conn,0)
    #for x in xrange(1,20):
    #    MySpiderThread(x,conn,m_cookies).start()    
    #    time.sleep(1)
    conn.close()



 
if __name__ == '__main__':
    #work()
    main()
    #print hash_id_to_num("69865e1245455c3bd3f0eeacdad64c5b")
    #create_tables()
    #conn=MySQLdb.connect(host="127.0.0.1",user="spider",passwd="spider123",db="zhihu_spider",charset="utf8")
    #get_user_info(conn,"69865e1245455c3bd3f0eeacdad64c5b")
    #mysql_test()

 
 