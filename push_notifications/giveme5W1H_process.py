# -*- coding: utf-8 -*-

from giveme5w1h import *
import pymysql
from datetime import date, timedelta,datetime
import time

def validate_summary(last_postid,lang_id):
    mydb1 = pymysql.connect(
      #host="49.156.128.100",
      host="192.168.1.98",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )
    
    mycursor1 = mydb1.cursor(pymysql.cursors.DictCursor)
    
    table="ugc_posts_local"
    #lang_id=1
    #query1="select * from {0} as t1 where t1.post_id > {1} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video') order by post_gmt".format(table,last_postid,lang_id)
    query1="select * from {0} as t1 where t1.post_id > {1} and t1.lang_id={2} and post_status='submittolocal' order by post_gmt".format(table,last_postid,lang_id)
    print(query1)
    mycursor1.execute(query1)    
    myresult1 = list(mycursor1.fetchall() )
    mycursor1.close()
    mydb1.close()
    
    if len(myresult1)>0:
        for post in myresult1:
            print(post["post_id"])
            text=post["post_text"]
            give5W1H(text)
            
        last_postid=myresult1[-1]["post_id"]
        
    return last_postid
    
mydb1 = pymysql.connect(
  #host="49.156.128.100",
  host="192.168.1.98",
  user="way2sms",
  passwd="waysmsawd#$%@",
  database="way2app",
  charset='utf8',
)

mycursor1 = mydb1.cursor(pymysql.cursors.DictCursor)

table="ugc_posts_local"
lang_id=1
today=str(date.today())
from_time=time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple())
query1="select * from {0} as t1 where t1.post_gmt > {1} and t1.lang_id={2} order by post_id limit 1".format(table,from_time,lang_id)
print(query1)
mycursor1.execute(query1)    
myresult1 = list(mycursor1.fetchall() )
mycursor1.close()
mydb1.close()

last_postid=myresult1[0]["post_id"]

#last_postid=3446218

#last_postid=validate_summary(last_postid)

while True:
    print("last_postid :: ",last_postid)
    last_postid=validate_summary(last_postid,lang_id)
    print("waiting for 10 seconds...")
    time.sleep(10)    

