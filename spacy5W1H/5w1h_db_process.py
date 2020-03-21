# -*- coding: utf-8 -*-
from get5W1H_with_translator import *
import pymysql
from datetime import date, timedelta,datetime
#import time
lang_codes={1:'te',2: 'ta',3: 'hi',4: 'kn',5: 'ml',6: 'mr',7: 'bn',8: 'gu',9: 'pa'}

def update_5w1h():
# =============================================================================
#     mydb = pymysql.connect(
#       host="49.156.128.100",
#       #host="192.168.1.98",
#       user="way2sms",
#       passwd="waysmsawd#$%@",
#       database="way2app",
#       charset='utf8',
#     )
# =============================================================================
    mydb = pymysql.connect(
      host="127.0.0.1",
      user="root",
      passwd="my$ql",
      database="new_schema",
      charset='utf8',
    )
    mycursor = mydb.cursor(pymysql.cursors.DictCursor)
    
    table="ugc_posts_local"
    #lang_id=8
    #today=str(date.today())
    #from_time=time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple())
    #query="select * from {0} as t1 where t1.post_gmt > {1} and lang_id=1 and t1.5w1h_status is null order by post_gmt limit 2".format(table,from_time)
    query='''SELECT * FROM {0} AS t1 WHERE lang_id=1 AND post_status='submit' AND post_date=CURRENT_DATE AND t1.5w1h_status IS NULL ORDER BY post_id LIMIT 100'''.format(table)
    print(query)
    mycursor.execute(query)    
    myresult = list(mycursor.fetchall() )
    mycursor.close()
    mydb.close()
    print("Number of posts: ",len(myresult))
    
    
    if len(myresult)>0:
# =============================================================================
#         mydb_w = pymysql.connect(
#           host="49.156.128.100",
#           #host="192.168.1.98",
#           user="way2sms",
#           passwd="waysmsawd#$%@",
#           database="way2app",
#           charset='utf8',
#         )
# =============================================================================
        mydb_w = pymysql.connect(
          host="127.0.0.1",
          user="root",
          passwd="my$ql",
          database="new_schema",
          charset='utf8',
        )
        mycursor_w = mydb_w.cursor(pymysql.cursors.DictCursor)
        
        table="ugc_posts_local"
        for doc in myresult:
            text=doc["post_text"]
            lang=lang_codes[doc["lang_id"]]
            result=extract_5W1H(text,lang)
            print(result)
            update_query='''update {0} set 5w1h_status="{1}" where post_id={2} limit 1'''.format(table,str(result),doc["post_id"])
            print(update_query)
            mycursor_w.execute(update_query)
            mydb_w.commit()
        mycursor_w.close()
        mydb_w.close()    
    else:
        print("No new posts")
    

update_5w1h()
# =============================================================================
# while True:
#     try:
#         update_5w1h()
#     except Exception as e:
#         print(e)
#     print("waiting for 10 seconds...")
#     time.sleep(10)
# 
# =============================================================================

