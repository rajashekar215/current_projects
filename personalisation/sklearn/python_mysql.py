# -*- coding: utf-8 -*-

import datetime
import time
import pandas as pd
import MySQLdb
from categories import *
from sklearn.externals import joblib
from operator import itemgetter


mydb = MySQLdb.connect(
  host="49.156.128.100",
  user="way2sms",
  passwd="waysmsawd#$%@",
  database="way2app",
  charset='utf8',
)

# =============================================================================
# mydb = mysql.connector.connect(
#   host="49.156.128.100",
#   user="way2sms",
#   passwd="waysmsawd#$%@",
#   database="way2app"
# )
#mycursor = mydb.cursor()
# =============================================================================
mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)

table="mag_posts_home_new"

# =============================================================================
# edition_states=(0,1)
# district_ids=(6,7,8)
# x = datetime.datetime.now()
# post_date=str(x).split(" ")[0]
# #mycursor.execute("select * from mag_posts_home_new where category_id != 2 and lang_id = 1 and edition_states in (0,1) and district_ids in (6,7,8) and post_date = '2019-02-25'")
# #print("select * from "+table+" where category_id != 2 and lang_id = "+str(lang_id)+" and edition_states in "+str(edition_states)+" and district_ids in "+str(district_ids)+" and post_date = '"+post_date+"'")
# #mycursor.execute("select * from "+table+" where category_id != 2 and lang_id = "+str(lang_id)+" and edition_states in ("+str(edition_states)+") and district_ids in ("+str(district_ids)+") and post_date = "+post_date)
# 
# statement = "SELECT * FROM {0}".format(table)
# if edition_states and district_ids:
#     statement += " WHERE category_id != 2 and lang_id = {0} and edition_states IN ({1}) and district_ids in ({2}) and post_date = '{3}' limit 100".format(
#         lang_id,', '.join(['%s'] * len(edition_states)),', '.join(['%s'] * len(district_ids)),post_date)
# #print(statement, edition_states,district_ids)
#mycursor.execute(statement, edition_states+district_ids)
# #where t1.post_gmt between UNIX_TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 5 day)) and UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id=? and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (t1.district_ids is null OR t1.district_ids REGEXP '(^|,)(" + userEditions + ")(,|$)') and t1.type is not null
# =============================================================================
# =============================================================================
# district_ids="6|7|8"
# query="select * from {0} as t1 where t1.post_gmt between UNIX_TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 5 day)) and UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={1} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (t1.district_ids is null OR t1.district_ids REGEXP '(^|,)({2})(,|$)') and t1.type is not null limit 1".format(table,lang_id,district_ids)
# 
# =============================================================================
t0=time.time()
lang_id=1
custid=17967799
query="select * from {0} as t1 where t1.post_gmt between UNIX_TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 0 day)) and UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={1} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null".format(table,lang_id)
print(query)
mycursor.execute(query)


myresult = mycursor.fetchall()  
#df=pd.DataFrame(myresult)
#df.columns = myresult.keys()
posts=[]
#post_data=[]
t1=time.time()-t0
print(t1)
t2=time.time()
for row in myresult:
    #print(row)
    post_doc=row
    key_query="SELECT lower(tag_name) as tag_name FROM way2app.mag_posts_home_tags_relation as t1 join way2app.mag_tags_home as t2 on t1.tag_id = t2.tag_id WHERE t1.post_id={0}".format(row['post_id'])
    mycursor.execute(key_query)
    key_result = mycursor.fetchall()
    post_doc['keywords']=[x['tag_name']for x in key_result]
    #print(post_doc)
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
    #print(pred[i])
    post_doc=myresult[i]
    #del post_doc['_id']
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

    
    
    
    
    
    
    
  
  

