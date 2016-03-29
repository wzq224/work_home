#coding=utf-8
#author:wzq
#date:2015-02-23

import os
import urllib
import urllib2
import re
import cookielib

HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',  
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36', 
        'Referer': 'http://www.zhihu.com/'}


def getHtml(url):
    page = urllib.urlopen(url);
    html = page.read();
    return html;



def getXsrf(url):
    html = getHtml2(url);   
    xsrf = re.search(r'(?<=name="_xsrf" value=")[^"]*(?="/>)', html)
    if xsrf == None:
        return ''
    else:
        return xsrf.group(0)


def getHtml2(url):


    
    req = urllib2.Request(url);
    #print req;
    page = urllib2.urlopen(req);
    html = page.read();
    return html;


    
def login():

    loginUrl = "http://www.zhihu.com/login/email";


    cj = cookielib.LWPCookieJar();
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPHandler)


    postDataArr={};
    xsrf = getXsrf("http://www.zhihu.com");
    postDataArr["_xsrf"]=xsrf;
    postDataArr["account"]="wzq.ok@foxmail.com";
    postDataArr["password"]="zhiqian123";
    postDataArr["rememberme"]="true";

    postData = urllib.urlencode(postDataArr) 

    urllib2.install_opener(opener)
    req = urllib2.Request(loginUrl,postData,HEADERS);
    
    conn = urllib2.urlopen(req);
    info = conn.info()
    
    opener.addheaders.append(('Cookie',info["Set-Cookie"]));
   
    return opener;


def zhihuTest1():
    #html =  getHtml2("http://www.zhihu.com/login/email");
    url="http://www.zhihu.com";
    html =  getHtml2(url);
    #print html;
    # print getXsrf(url);
    # f = open("a.txt","w");
    # f.write(html)
    # f.close();




def main():
    #zhihuTest1();

    opener = login();
    print opener;
    f = opener.open("https://www.zhihu.com/people/kk-ko-74/followees")
    print f.getcode();
    html = f.read();



    f = open("nonn.html","w");
    f.write(html)
    f.close();


if __name__ == '__main__':
    main()