# -*- coding: utf-8 -*-

import datetime
import time
import pandas as pd
import MySQLdb
from categories import *
from sklearn.externals import joblib
from operator import itemgetter




def predictions(custid):
    mydb = MySQLdb.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )
    
    mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    
    table="mag_posts_home_new"
    t0=time.time()
    lang_id=1
    #custid=17967798
    query="select * from {0} as t1 where t1.post_gmt between UNIX_TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 0 day)) and UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={1} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null".format(table,lang_id)
    #print(query)
    mycursor.execute(query)    
    myresult = mycursor.fetchall()  
    posts=[]
    t1=time.time()-t0
    print(t1)
    t2=time.time()
    for row in myresult:
        post_doc=row
        key_query="SELECT lower(tag_name) as tag_name FROM way2app.mag_posts_home_tags_relation as t1 join way2app.mag_tags_home as t2 on t1.tag_id = t2.tag_id WHERE t1.post_id={0}".format(row['post_id'])
        mycursor.execute(key_query)
        key_result = mycursor.fetchall()
        post_doc['keywords']=[x['tag_name']for x in key_result]
        s=''
        if "category_name" in post_doc and post_doc["category_name"]: s=s+cat[post_doc["category_name"]] if post_doc["category_name"] in cat else post_doc["category_name"]
        if "keywords" in post_doc and post_doc["keywords"]: s=s+" "+" ".join(post_doc["keywords"])
        posts.append(s)
    
    #print(posts)
    t3=time.time()-t2
    print(t3)
    t4=time.time()
    model=joblib.load("../models/"+str(custid))
    pred=model.predict(posts)
    t5=time.time()-t4
    print(t5)
    ins_array=[]
    for i in range(len(pred)):
        post_doc=myresult[i]
        del post_doc['post_date']
        #postid=post_doc['postid']
        #post_doc['postid']=int(postid)
        post_doc['custid']=custid
        post_doc['prediction']=int(pred[i])
        #print(post_doc)
        ins_array.append(post_doc)
    #print(ins_array)
    ins_array = sorted(ins_array, key=itemgetter('prediction'), reverse=True)
    #print(ins_array)
    t6=time.time()-t0
    print(t6)
    mycursor.close()
    mydb.close()
    return ins_array