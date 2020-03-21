# -*- coding: utf-8 -*-
import pymysql

lang_id=1

mydb = pymysql.connect(
  host="49.156.128.100",
  user="way2sms",
  passwd="waysmsawd#$%@",
  database="way2app",
  charset='utf8',
)

   
mycursor = mydb.cursor(pymysql.cursors.DictCursor)

q1="select post_id from post_match_score where match_status=0 and lang_id={0}".format(lang_id)
print(q1)
mycursor.execute(q1)    
pull_back_result = mycursor.fetchall()

pull_back_post_ids=tuple(doc["post_id"] for doc in pull_back_result)

q2="select * from mag_posts_home_new where post_id in (%s)"
print(q2)
mycursor.execute(q2,pull_back_post_ids)    
check_posts1 = mycursor.fetchall()


q3="select post_id from post_match_score where lang_id=1 order by post_id desc limit 1".format(lang_id)
print(q3)
mycursor.execute(q3)    
last_post_id= mycursor.fetchall()[0]["post_id"]

q4="select * from mag_posts_home_new where post_id > {0} and lang_id={1} limit 100".format(last_post_id,lang_id)
print(q4)
mycursor.execute(q4)    
check_posts2 = mycursor.fetchall()

total_check_posts=check_posts1+check_posts2

mycursor.close()
mydb.close()



#loop 





