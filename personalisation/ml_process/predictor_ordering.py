# -*- coding: utf-8 -*-

import datetime
import time
import pandas as pd
import MySQLdb
from categories import *
from sklearn.externals import joblib
from operator import itemgetter
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn import linear_model
from pymongo import MongoClient
from pprint import pprint



def predictions(custid):
    client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
    mdb=client["way2"]
    user_rating_collection="user_data"
    user_keyword_collection="user_keywords_data"
    
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
    fields="t1.post_id as postid,t1.post_id_encrypted,t1.writer_name,t1.lang_id as lang,t1.source_id as sourceid,t1.post_title as posttitle,post_date AS publishdate,DATE_FORMAT(FROM_UNIXTIME(t1.post_gmt), '%Y-%m-%d %H:%i:%S') AS timediff,DATE_FORMAT(CURRENT_TIMESTAMP,'%Y-%m-%d %H:%i:%S') AS timediff1, DATEDIFF(CURRENT_DATE, DATE(FROM_UNIXTIME(t1.post_gmt))) AS daysdiff, t1.source_name as sourcename,t1.category_id as categoryid,t1.post_url as longdescurl,t1.post_desc as longdesc, t1.show_button,t1.button_url, t1.news_type, t1.btn_border_color, t1.btn_bg_color, t1.btn_font_color, t1.btn_text, t1.btn_text_lang, t1.img_url as imgurl, t1.video_url as videourl,t1.img_height as height, t1.img_width as width, t1.font_color, t1.top_color, t1.bottom_color, t1.imgs_count,t1.post_status, t1.type, t1.is_ad, t1.comments_flag, t1.whatsapp_share_count, t1.fb_share_count, t1.post_parent, t1.city_ids, t1.plus18_post, t1.hashtag_id, t1.1time_sticky_pos,t1.res2,t1.brand_logo,t1.brand_url, t1.btn_share_content, t1.category_name, t1.dfp_code, t1.impr_url, t1.writer_custid, t1.writer_image, t1.writer_level, t1.writer_topic, t1.writer_sub_topic"
    query="select "+fields+" from {0} as t1 where t1.post_gmt between UNIX_TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 0 day)) and UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={1} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null".format(table,lang_id)
    #print(query)
    mycursor.execute(query)    
    myresult = mycursor.fetchall()  
    posts=[]
    t1=time.time()-t0
    print(t1)
    t2=time.time()
    for row in myresult:
        post_doc=row
        key_query="SELECT lower(tag_name) as tag_name FROM way2app.mag_posts_home_tags_relation as t1 join way2app.mag_tags_home as t2 on t1.tag_id = t2.tag_id WHERE t1.post_id={0}".format(row['postid'])
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
    vectorizer = HashingVectorizer()
    #vectorizer=joblib.load("../models/vect_"+str(custid))
    vect_posts=vectorizer.transform(posts)
    model=joblib.load("../models/"+str(custid))
    pred=model.predict(vect_posts)
    t5=time.time()-t4
    print(t5)
    test_pred=model.predict(vectorizer.transform(["News chandrababu"]))
    #print("testtt  ",test_pred)
    
    
    ins_array=[]
    for i in range(len(pred)):
        post_doc=myresult[i]
        #del post_doc['post_date']
        #postid=post_doc['postid']
        #post_doc['postid']=int(postid)
        post_doc['custid']=custid
        post_doc['prediction']=int(pred[i])
        
        #print(post_doc)
        ins_array.append(post_doc)
    #print(ins_array)
    #ins_array = sorted(ins_array, key=itemgetter('prediction','post_gmt'), reverse=True)
    ins_array = sorted(ins_array, key=itemgetter('prediction'), reverse=True)
    #print(ins_array)
    
    x = datetime.datetime.now()
    today_date=str(x).split(" ")[0]
    #print(type(custid),type(today_date))
    seen_docs=mdb[user_rating_collection].find({"custid" : int(custid),"date" :{'$in':[today_date]}},{"_id":0,"postid":1})
    sp=[]
    for pid in seen_docs:
         sp.append(pid["postid"])
    cat_list=list(mdb[user_keyword_collection].find({"custid" : int(custid)},{"_id":0,"category":1}))
    #print(cat_list)
    cat_list=cat_list[0]["category"]     
    cat_list=dict(sorted(cat_list.items(),key=itemgetter(1),reverse=True))
    #print(cat_list)
    cat_list=list(cat_list.keys())
    try:
        cat_list.remove("News")
        cat_list.remove("undefined")
        cat_list.append("News")
        cat_list.apped("undefined") 
    except:
        pass
    #print(cat_list)
    seen_posts=[]
    unseen_rated_posts=[]
    unseen_unrated_posts=[]
    c=[]
    for p in ins_array:
        if "category_name" in p and p["category_name"]:
            if p["category_name"] in cat: 
                if cat[p["category_name"]] not in c:
                    c.append(cat[p["category_name"]])
                p["category_name"]=cat[p["category_name"]] 
            else:
                c.append(p["category_name"]);
        if p["postid"] in sp:
            seen_posts.append(p)
        else:
            if p["prediction"]>0:
                unseen_rated_posts.append(p)
            else:
                unseen_unrated_posts.append(p)
    for e in cat_list:
        try:
            c.remove(e)
        except:
            pass
    cat_list=list(cat_list)
    cat_list.extend(c)
    #print(cat_list)            
    srt = {b: i for i, b in enumerate(cat_list)}
    unseen_unrated_posts=sorted(unseen_unrated_posts, key=lambda x: srt[x["category_name"]])
    final_array=[]
    final_array.extend(unseen_rated_posts)
    final_array.extend(unseen_unrated_posts)
    final_array.extend(seen_posts)
    
    t6=time.time()-t0
    print(t6)
    mycursor.close()
    mydb.close()
    client.close()
    zeros=["daysdiff", "categoryid", "show_button", "postid", "btn_text_lang", "writer_custid", "is_ad", "whatsapp_share_count", "fb_share_count", "imgs_count", "sourceid", "lang", "post_parent"]
    for post_doc in final_array:
        for key in post_doc:
            
            if key in post_doc and post_doc[key] is not None:post_doc[key]=str(post_doc[key]) 
            if key in zeros and not post_doc[key]:
                post_doc[key]=str(0)
    return final_array[:5]


#pprint(predictions(17511156)[0])
