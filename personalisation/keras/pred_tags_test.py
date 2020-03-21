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
import numpy as np
import re
from keras.models import load_model
import pymysql
from categoryapi import *
from indic_tagger.pipeline import *


def clean_text(text):
    line = text.split(' ')
    new_doc=[]
    for w in line:
        w=re.sub('\s*\d*\s', '', w)
        match_string="[☛.,'\":?<>&\r\n#\s\d;*\-!()/\$]"
        unmatch_string="[^☛.,'\":?<>&\r\n#\s\d;*\-!()/\$]"
        if re.search('(^'+match_string+'|'+match_string+'*$)',w):
                    #print("wordddd",w)
                    try:
                        start = re.search('(^'+match_string+'*)',w).group()
                        #print("start",start)
                        w = w.replace(start,"")
                    except:
                        pass
                    try:
                        end = re.search('('+match_string+'*$)',w).group()
                        #print("end",end)
                        w = w.replace(end, "")
                    except:
                        pass
        else:
            pass
            #print("no special chars",w)
#             print(w)                           
        if w is not "":
            try:
                #print("word  ",w)
                middle = re.findall(unmatch_string+'*('+match_string+'+)',w)
                #print("middle  ",middle)
                for m in middle:
                    if m!='':
                        w = w.replace(m," ")
                w=w.split(" ")
                #print("split  ",w)
                if w is not "":
                    new_doc.extend(w)
            except:
                new_doc.append(w)
    return ' '.join(new_doc)
# =============================================================================
# import time
# vt=time.time()
# from telugu_word_embeddings import *
# print("vector loading time:: ",time.time()-vt)
# =============================================================================


client = MongoClient('mongodb://localhost:27017')    
mdb=client["way2_personalize"]


mydb = pymysql.connect(
  host="49.156.128.100",
  user="way2sms",
  passwd="waysmsawd#$%@",
  db="way2app",
  charset='utf8',
)

mycursor = mydb.cursor(pymysql.cursors.DictCursor)

custid=22172222
lang_id=1
categoryid=0
request_source=""
userEditions=""
userMandals="0"
userVillages="0"
singleDistrict="no"


skip=0
limit=8
today_date=str(datetime.datetime.fromtimestamp(int(time.time()))).split(" ")[0]
from_time=str(time.mktime(datetime.datetime.strptime(today_date, "%Y-%m-%d").timetuple()))
to_time=str(time.time())
print(skip,limit)


#from_time=str(from_time)
#to_time=str(to_time)
#table="mag_posts_home_new"
#t0=time.time()

  
        
print("langidddd",lang_id)
queryGetParams = "t1.post_id as postid,t1.post_id_encrypted,t1.writer_name,t1.lang_id as lang,t1.source_id as sourceid,t1.post_title as posttitle,t1.post_gmt,post_date AS publishdate,DATE_FORMAT(FROM_UNIXTIME(t1.post_gmt), '%Y-%m-%d %H:%i:%S') AS timediff,DATE_FORMAT(CURRENT_TIMESTAMP,'%Y-%m-%d %H:%i:%S') AS timediff1, DATEDIFF(CURRENT_DATE, DATE(FROM_UNIXTIME(t1.post_gmt))) AS daysdiff, t1.source_name as sourcename,t1.category_id as categoryid,t1.post_url as longdescurl,t1.post_desc as longdesc, t1.show_button,t1.button_url, t1.news_type, t1.btn_border_color, t1.btn_bg_color, t1.btn_font_color, t1.btn_text, t1.btn_text_lang, t1.img_url as imgurl, t1.video_url as videourl,t1.img_height as height, t1.img_width as width, t1.font_color, t1.top_color, t1.bottom_color, t1.imgs_count,t1.post_status, t1.type, t1.is_ad, t1.comments_flag, t1.whatsapp_share_count, t1.fb_share_count, t1.post_parent, t1.city_ids, t1.plus18_post, t1.hashtag_id, t1.1time_sticky_pos,t1.res2,t1.brand_logo,t1.brand_url, t1.btn_share_content, t1.category_name, t1.dfp_code, t1.impr_url, t1.writer_custid, t1.writer_image, t1.writer_level, t1.writer_topic, t1.writer_sub_topic,t1.is_breaking";
#query ="SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between UNIX_TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 5 day)) and " + currentPostTime + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={0} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null order by t1.post_gmt desc".format(lang_id)
if categoryid == 0 or categoryid == -1:
    if lang_id == 3 or lang_id == 11:
        if not request_source=="":
            if singleDistrict=="yes":
                print("qqqqqqqqqqqqqqqqq",1)
                query = "SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between "+from_time+" and " + to_time + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id="+str(lang_id)+" and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids REGEXP '(^|,)(" + userEditions + ")(,|$)' and (t1.mandal_id=0 OR t1.mandal_id REGEXP '(^|,)(" + userMandals + ")(,|$)') and (t1.village_id=0 OR t1.village_id REGEXP '(^|,)(" + userVillages + ")(,|$)') and t1.type is not null order by t1.post_gmt desc"
            else:
                print("qqqqqqqqqqqqqqqqq",2)
                query = "SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between "+from_time+" and " + to_time + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id="+str(lang_id)+" and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (t1.district_ids is null OR t1.district_ids REGEXP '(^|,)(" + userEditions + ")(,|$)') and (t1.mandal_id=0 OR t1.mandal_id REGEXP '(^|,)(" + userMandals + ")(,|$)') and (t1.village_id=0 OR t1.village_id REGEXP '(^|,)(" + userVillages + ")(,|$)') and t1.type is not null order by t1.post_gmt desc"
        else :  #news
            print("qqqqqqqqqqqqqqqqq",3)
            query = "SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between "+from_time+" and " + to_time + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id="+str(lang_id)+" and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null order by t1.post_gmt desc"
    else:
        if not request_source=="":
            if singleDistrict=="yes":
                print("qqqqqqqqqqqqqqqqq",4)
                query = "SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between "+from_time+" and " + to_time + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id="+str(lang_id)+" and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids REGEXP '(^|,)(" + userEditions + ")(,|$)' and (t1.mandal_id=0 OR t1.mandal_id REGEXP '(^|,)(" + userMandals + ")(,|$)') and (t1.village_id=0 OR t1.village_id REGEXP '(^|,)(" + userVillages + ")(,|$)') and t1.type is not null order by t1.post_gmt desc"
            else:
                print("qqqqqqqqqqqqqqqqq",5)
                query ="SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between "+from_time+" and " + to_time + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id="+str(lang_id)+" and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (t1.district_ids is null OR t1.district_ids REGEXP '(^|,)(" + userEditions + ")(,|$)') and (t1.mandal_id=0 OR t1.mandal_id REGEXP '(^|,)(" + userMandals + ")(,|$)') and (t1.village_id=0 OR t1.village_id REGEXP '(^|,)(" + userVillages + ")(,|$)') and t1.type is not null order by t1.post_gmt desc"
        else:   #news
            print("qqqqqqqqqqqqqqqqq",6)
            query ="SELECT " + queryGetParams + " FROM mag_posts_home_new as t1  where t1.post_gmt between "+from_time+" and " + to_time + " AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id="+str(lang_id)+" and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null order by t1.post_gmt desc"
elif categoryid == 2 and request_source not in ("","0"):
    print("qqqqqqqqqqqqqqqqq",7)
    query = "SELECT " + queryGetParams + " FROM mag_posts_home_new as t1 where t1.post_gmt between "+from_time+" and " + to_time + " and t1.lang_id={1} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null and source_id={2} order by t1.post_gmt desc".format(categoryid,lang_id,request_source)
else:#for categories
    print("qqqqqqqqqqqqqqqqq",8)
    query = "SELECT " + queryGetParams + " FROM mag_posts_home_new as t1 where t1.post_gmt between "+from_time+" and " + to_time + " and t1.category_id={0} and t1.lang_id={1} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and t1.district_ids is null and t1.type is not null order by t1.post_gmt desc".format(categoryid,lang_id)
#print(query)
mycursor.execute(query)    
myresult = mycursor.fetchall() 



#client_103 = MongoClient('mongodb://49.156.128.103:27017/?readPreference=secondaryPreferred')
client_103 = MongoClient('mongodb://49.156.128.103:27017/?readPreference=secondaryPreferred')
mdb_103=client_103["way2"]
#user_rating_collection="user_data_new"
#user_keyword_collection="newsreg-user-keywords-data"
#posts=[]
breaking=[]
push_posts=[]
predict_posts=[]
seen_posts=[]
#    t1=time.time()-t0
#    print(t1)
   # t2=time.time()
x = datetime.datetime.now()
today_date=str(x).split(" ")[0]
#print('track_posts_cat_'+str(today_date.split("-")[2]).replace("^0","")+"_"+str(today_date.split("-")[1]).replace("^0","")+"_"+today_date.split("-")[0])
print('track_posts_cat_'+str(today_date.split("-")[2]).lstrip('0')+"_"+str(today_date.split("-")[1]).lstrip('0')+"_"+today_date.split("-")[0])
seen_docs=mdb_103['track_posts_cat_'+str(today_date.split("-")[2]).lstrip('0')+"_"+str(today_date.split("-")[1]).lstrip('0')+"_"+today_date.split("-")[0]].find({"custid":int(custid)})
#seen_docs=mdb[user_rating_collection].find({"custid" : int(custid),"date" :{'$in':[today_date]}},{"_id":0,"postid":1})
sp=[]
for pid in seen_docs:
    #print(pid)
    sp.append(pid["postid"])
client_103.close()
print("seen pids:: ",sp)
   
current_loop_date=str(datetime.datetime.fromtimestamp(float(from_time))).split(" ")[0]
push_query="SELECT post_id FROM push_notifications_queue WHERE lang_id=1 AND  push_date='"+current_loop_date+"'"
mycursor.execute(push_query)
push_result = mycursor.fetchall()
push_ids=[]


for doc in push_result:
    #print("pushhhh",doc)
    push_ids.append(doc["post_id"])
    

text_X=[]
cat_X=[]
key_X=[]        
for row in myresult:
    #if(row['postid'])==1958817 and row["is_breaking"]==1 and str(row["publishdate"])==today_date:
        #print(row)
    if "is_breaking" in row and row["is_breaking"]==1 and str(row["publishdate"])==current_loop_date:
        if row['postid'] in sp:
            seen_posts.append(row)
        else:
            breaking.append(row)
    elif "news_type" in row and row["news_type"]=="breaking" and str(row["publishdate"])==current_loop_date:
        if row['postid'] in sp:
            seen_posts.append(row)
        else:
            breaking.append(row)
    elif row['postid'] in push_ids:
        if row['postid'] in sp:
            seen_posts.append(row)
        else:
            push_posts.append(row)
    else:
        post_doc=row
        key_query="SELECT post_id,lower(tag_name) as tag_name FROM way2app.mag_post_mechine_tags WHERE post_id={0}".format(row['postid'])
        mycursor.execute(key_query)
        key_result = mycursor.fetchall()
        post_doc['keywords']=[x['tag_name']for x in key_result]
        
# =============================================================================
#             s=''
#             #if "category_name" in post_doc and post_doc["category_name"]: s=s+cat[post_doc["category_name"]] if post_doc["category_name"] in cat else post_doc["category_name"]
#             if "keywords" in post_doc and post_doc["keywords"]: s=s+" "+" ".join(post_doc["keywords"])
#             if "longdesc" in doc and doc["longdesc"]:
#                 s=s+" "+category(doc["longdesc"])
#                 s=s+" "+doc["longdesc"]
#             posts.append(s)
# =============================================================================
        s=''
        catg=''
        keys=''
        #if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
# =============================================================================
#         if "keywords" in post_doc and post_doc["keywords"]:
#             #s=s+" "+" ".join(doc["keywords"])
#             keys=keys+" ".join(post_doc["keywords"])
#         else:
#             keys="Nothing"
# =============================================================================
        if "longdesc" in post_doc and post_doc["longdesc"] and post_doc["longdesc"]!='':
            #s=s+" "+category(doc["post_desc"])
            s=clean_text(post_doc["longdesc"])
            catg=catg+category(s)
            row["ai_cat"]=catg
            tags=getTaggers(s,"te")
            if 'NN' in tags and len(tags['NN'])>0:
                keys=keys+' '.join(tags['NN'])
            if 'NNP' in tags and len(tags['NNP'])>0:
                keys=keys+" "+' '.join(tags['NNP'])
        else:
            if "category" in post_doc and post_doc["category"]: catg=catg+cat[post_doc["category"]] if post_doc["category"] in cat else post_doc["category"]
            else:catg="Nothing"
            if "posttitle" in post_doc and post_doc["posttitle"] and post_doc["posttitle"]!='':
                    s=clean_text(post_doc["posttitle"])
                    tags=getTaggers(s,"te")
                    if 'NN' in tags and len(tags['NN'])>0:
                        keys=keys+' '.join(tags['NN'])
                    if 'NNP' in tags and len(tags['NNP'])>0:
                        keys=keys+" "+' '.join(tags['NNP'])

        if s=='':
            s="Nothing"
        if keys=='':
            keys="Nothing"
        text_X.append(s)
        cat_X.append(catg)
        key_X.append(clean_text(keys))
        predict_posts.append(row)
        
b_ids= [d['postid'] for d in breaking]  
p_ids=  [d['postid'] for d in push_posts]       
print(b_ids,p_ids)

break_plus_push=[]
break_plus_push.extend(breaking)
break_plus_push.extend(push_posts)
break_plus_push = sorted(break_plus_push, key=itemgetter('post_gmt'), reverse=True)


# =============================================================================
# cleaned_text_X=[]
# for d in text_X:    
#     cleaned_text_X.append(clean_text(d))
#     
# cleaned_key_X=[]
# for c in key_X:    
#     cleaned_key_X.append(clean_text(c))    
# =============================================================================
      
        
cleaned_text_X=text_X

cleaned_key_X=key_X
          
# =============================================================================
#     EMBEDDING_DIM=300
#     MAX_SEQUENCE_LENGTH=100
#     
#     final_input_matrix_test=np.zeros((len(cleaned_test_X),MAX_SEQUENCE_LENGTH, EMBEDDING_DIM))        
#     i=0
#     for p in cleaned_test_X:
#         awords=p.split(" ")
#         j=0
#         for w in awords:
#             embedding_vector = embeddings_index.get(w)
#             if embedding_vector is not None:
#                 # words not found in embedding index will be all-zeros.
#                 final_input_matrix_test[i][j] = embedding_vector
#             j=j+1
#         i=i+1
# =============================================================================
EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

final_text_matrix=np.zeros((len(cleaned_text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in cleaned_text_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_text_matrix[i][j] = embedding_vector
        j=j+1
        if j==60: break
    i=i+1
    
final_text_matrix[final_text_matrix==0]=np.nan


MAX_CAT_LENGTH=4

final_cat_matrix=np.zeros((len(cleaned_text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
i=0
for p in cat_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_cat_matrix[i][j] = embedding_vector
        j=j+1
    i=i+1
    
final_cat_matrix[final_cat_matrix==0]=np.nan

MAX_KEY_LENGTH=60

final_key_matrix=np.zeros((len(cleaned_text_X),MAX_KEY_LENGTH, EMBEDDING_DIM))        
i=0
for p in cleaned_key_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_key_matrix[i][j] = embedding_vector
        j=j+1
        if j==60: break
    i=i+1
    
final_key_matrix[final_key_matrix==0]=np.nan


    
final_sentence_matrix=np.zeros((len(cleaned_text_X),3, EMBEDDING_DIM))        


for p in range(len(cleaned_text_X)):
    final_sentence_matrix[p][0]=np.nanmean(final_key_matrix[p],axis=0)
    final_sentence_matrix[p][1]=np.nanmean(final_cat_matrix[p],axis=0)
    final_sentence_matrix[p][2]=np.nanmean(final_text_matrix[p],axis=0)
    
    
final_sentence_matrix[np.isnan(final_sentence_matrix)] = 0


try:
    print("old user "+str(custid))
    model=load_model("../models_tags/"+str(custid))
    pred=model.predict_classes(final_sentence_matrix)

   # t5=time.time()-t4
   # print(t5)
    #test_pred=model.predict(vectorizer.transform(["News chandrababu"]))
    #print("testtt  ",test_pred)
    
    
    ins_array=[]
    for i in range(len(pred)):
        post_doc=predict_posts[i]
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
    
   
    #print(type(custid),type(today_date))
    
# =============================================================================
#         cat_list=list(mdb[user_keyword_collection].find({"custid" : int(custid)},{"_id":0,"category":1}))
#         #print(cat_list)
#         cat_list=cat_list[0]["category"]     
#         cat_list=dict(sorted(cat_list.items(),key=itemgetter(1),reverse=True))
#         #print(cat_list)
#         cat_list=list(cat_list.keys())
#         try:
#             cat_list.remove("News")
#             cat_list.remove("undefined")
#             cat_list.append("News")
#             cat_list.apped("undefined") 
#         except:
#             pass
#         #print(cat_list)
# =============================================================================
    
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
                if p["category_name"] not in c:c.append(p["category_name"]);
        
        if p["postid"] in sp:
            seen_posts.append(p)
        else:
            if p["prediction"]>0:
                    unseen_rated_posts.append(p)
            else:
                    unseen_unrated_posts.append(p)    
# =============================================================================
#         for e in cat_list:
#             try:
#                 c.remove(e)
#             except:
#                 pass
#         cat_list=list(cat_list)
#         cat_list.extend(c)
#         cat_list.append(None)
#         print(cat_list)
#         #pprint(unseen_unrated_posts)            
#         srt = {b: i for i, b in enumerate(cat_list)}
#         unseen_unrated_posts=sorted(unseen_unrated_posts, key=lambda x: srt[x["category_name"]])
#         
# =============================================================================
    final_array=[]
    #final_array.extend(breaking)
    #final_array.extend(push_posts)
    final_array.extend(break_plus_push)
    final_array.extend(unseen_rated_posts)
    final_array.extend(unseen_unrated_posts)
    final_array.extend(seen_posts)
    s_ids=  [d['postid'] for d in seen_posts]       
    print(s_ids)
  #  t6=time.time()-t0
   # print(t6)
    unseen_length=len(break_plus_push)+len(unseen_rated_posts)+len(unseen_unrated_posts)
    print("old user","unseen::",unseen_length,"seen",len(seen_posts),"skip::",skip,"limit::",limit)
    print("break_plus_push:: ",len(break_plus_push),"  unseen_rated_posts:: ",len(unseen_rated_posts)," unseen_unrated_posts:: ",len(unseen_unrated_posts))
except:
    print("new user  ",custid)
    unseen_posts=[]
    for p in predict_posts:
        if p["postid"] in sp:
             seen_posts.append(p)
        else:
             unseen_posts.append(p)
    final_array=[]
    final_array.extend(break_plus_push)
    final_array.extend(unseen_posts)
    final_array.extend(seen_posts)
    unseen_length=len(break_plus_push)+len(unseen_posts)
    print("new user","unseen::",unseen_length,"seen",len(seen_posts),"skip::",skip,"limit::",limit)
    print("break_plus_push:: ",len(break_plus_push),"  unseen_posts:: ",len(unseen_posts))
zeros=["daysdiff", "categoryid", "show_button", "postid", "btn_text_lang", "writer_custid", "is_ad", "whatsapp_share_count", "fb_share_count", "imgs_count", "sourceid", "lang", "post_parent"]
for post_doc in final_array:
    for key in post_doc:
        
        if key in post_doc and post_doc[key] is not None:post_doc[key]=str(post_doc[key]) 
        if key in zeros and not post_doc[key]:
            post_doc[key]=str(0)
            
f_ids=  [d['postid'] for d in final_array]       
print(f_ids)
#return final_array[skip:skip+limit]
#return final_array
