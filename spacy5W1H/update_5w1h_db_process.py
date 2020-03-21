# -*- coding: utf-8 -*-
from get5W1H_with_translator import *
import configparser
#import RawConfigParser
import pymysql
from datetime import date, timedelta,datetime
import time
config = configparser.RawConfigParser()
#config = RawConfigParser.ConfigParser()
config.read('5w1h_config.ini')
lang_codes={1:'te',2: 'ta',3: 'hi',4: 'kn',5: 'ml',6: 'mr',7: 'bn',8: 'gu',9: 'pa'}


def update_5w1h():
    mydb = pymysql.connect(
      host=config['mysqlDB_read']['host'],
      user=config['mysqlDB_read']['user'],
      passwd=config['mysqlDB_read']['passwd'],
      database=config['mysqlDB_read']['database'],
      charset=config['mysqlDB_read']['charset'],
    )
    mycursor = mydb.cursor(pymysql.cursors.DictCursor)
    
    read_table=config['mysqlDB_read']['table']
    #lang_id=8
    #today=str(date.today())
    #from_time=time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple())
    #query="select * from {0} as t1 where t1.post_gmt > {1} and lang_id=1 and t1.5w1h_status is null order by post_gmt limit 2".format(table,from_time)
    #query='''SELECT * FROM {0} AS t1 WHERE lang_id=1 AND post_status='submit' AND post_date=CURRENT_DATE AND t1.5w1h_status IS NULL ORDER BY post_id LIMIT 1'''.format(read_table)
    query='''SELECT * FROM {0} AS t1 WHERE lang_id=1  AND post_date=CURRENT_DATE ORDER BY post_id LIMIT 100'''.format(read_table)
    print(query)
    mycursor.execute(query)    
    myresult = list(mycursor.fetchall() )
    mycursor.close()
    mydb.close()
    print("Number of posts: ",len(myresult))
    
    
    if len(myresult)>0:
        
        for doc in myresult:
            text=doc["post_text"]
            lang=lang_codes[doc["lang_id"]]
            result=extract_5W1H(text,lang)
            print(result)
            write_table=config['mysqlDB_write']['table']
            update_query='''update {0} set 5w1h_status="{1}" where post_id={2} limit 1'''.format(write_table,str(result),doc["post_id"])
            print(update_query)
            mydb_w = pymysql.connect(
              host=config['mysqlDB_write']['host'],
              user=config['mysqlDB_write']['user'],
              passwd=config['mysqlDB_write']['passwd'],
              database=config['mysqlDB_write']['database'],
              charset=config['mysqlDB_write']['charset'],
            )
            mycursor_w = mydb_w.cursor(pymysql.cursors.DictCursor)
            mycursor_w.execute(update_query)
            mydb_w.commit()
            mycursor_w.close()
            mydb_w.close()    
    else:
        print("No new posts")
        print("waiting for 10 seconds...")
        time.sleep(10)
    

#update_5w1h()
while True:
    try:
        update_5w1h()
    except Exception as e:
        print(e)


