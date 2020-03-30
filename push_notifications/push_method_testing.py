# -*- coding: utf-8 -*-
import pymysql
from datetime import date, timedelta,datetime
import time
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

import configparser
config = configparser.RawConfigParser()
config.read('push_config.ini')

from load_word_embeddings import * 

stopwords =[]#["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి", "తెలిపారు","ఆయన","రూ","సందర్భంగా","పాల్గొన్నారు","అన్నారు","న","దీంతో","నిర్వహించారు","ఏర్పాటు","వ","లో","చేయాలని","పేర్కొన్నారు","చేసింది","కోరారు","చేసి","తెలిపింది","ఆమె","చెప్పారు","చేస్తున్నారు","జరిగింది","తర్వాత","వెంటనే","వెల్లడించారు","ఏ","మాత్రమే","కోరుతున్నారు","తెలుస్తోంది","తెలిసిందే","తాను","కు","ఇప్పటికే","ఎలాంటి","నిర్వహించిన","దీనిపై","ఇటీవల","ఇది","చేసే","తీసుకోవాలని","పేర్కొంది","చేపట్టారు","చేస్తున్న","గో","చేసినట్లు","చేయడం","మాత్రం","ఉండగా","ఇక","చేసేందుకు","ఇందులో","చేశాడు","తనకు","ఇచ్చారు","చేస్తామని","ను","ఇచ్చిన","చేస్తూ","జరుగుతున్న","గా","మీ","అలాగే","చేసుకోవాలని","ఇవ్వాలని","చేయగా","తో","తమకు","ఉండాలని","ఉండే","ఇదే","తూ","చేస్తున్నట్లు","వచ్చి","వాటిని","ఇప్పుడు","చేసుకున్నారు","ఉంటే","ఉన్నాయి","చేస్తే","ఉంటుంది","వేసి","అంటూ","చేసుకుంది","ఇలా","తనను","వెళ్లి","అయిన","మాట్లాడుతూ","చేపట్టిన","తెలిపాడు","వస్తున్న","కానుంది","ఉండటంతో","చేసుకున్న","అందించారు","ఇలాంటి","వచ్చింది","అదే","మన","వే","దీన్ని","తీసుకున్నారు","అందులో","కావాలని","అందరూ","ఉన్నాయని","చేయనున్నారు","చేయనున్నట్లు","చేసారు","మాట్లాడారు","అక్కడ","అండ్","ఉ","చేసుకుని","నా","ఉందన్నారు","అందరికీ","చేస్తానని","ఆయనకు","చేస్తోంది","నేను","చేశామని","ఇందుకు","ఇక్కడ","చేస్తామన్నారు","చెబుతున్నారు","దీనిని","ని","అందుకే","ఇప్పటి","చెప్పాడు","మా","వాటి","ఉంటాయని","అంటున్నారు","చేయనుంది","అయింది","అన్న","తేది","ఎన్ని","తమను","అన్నాడు","ఎప్పుడు","చేస్తుండగా","చేసుకున్నాడు","ఎప్పుడూ","చేస్తుందని","చేస్తుంది","చేస్తున్నామని","దాన్ని","చేశామన్నారు","చేస్తున్నాయి","చెప్తున్నారు","ల","ఢీ","అందిస్తామని","చేస్తారని","చేసిందని","అవుతుంది","అందుకు","చేస్తారు","అతను","చేపట్టింది","చేస్తోందని","చేసుకోవచ్చని","చేసుకోవచ్చు","చేయనున్న","మీకు","చేస్తున్నాం","గారు","మండలం","లోని","గారి","లు","గారిని","గారికి","లకు","లోకి","జి","వారిని","చేయుచున్నారు"]
     
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
                    new_doc.extend([ww for ww in w if ww!=""])
            except:
                if w!="":
                    new_doc.append(w)
    return ' '.join(new_doc).replace("\u200c"," ")

def get_sentence_vector(words,MAX_TEXT_LENGTH, EMBEDDING_DIM):
    text_array=np.zeros((MAX_TEXT_LENGTH, EMBEDDING_DIM))
    j=0
    for w in words:
        embedding_vector = embeddings_index.get(w)
        #embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            text_array[j] = embedding_vector
            #text_array[j] = embedding_vector.decode().split(" ")
        j=j+1
        if j==60: break 
    
    text_array[text_array==0]=np.nan
    text_array=np.nanmean(text_array,axis=0)
    text_array[np.isnan(text_array)] = 0    
    return text_array

def prepare_push_users(last_post_gmt):
    EMBEDDING_DIM=300
    MAX_TEXT_LENGTH=60
    mydb1 = pymysql.connect(
      host=config["mysqlDB_read"]["host"],
      user=config["mysqlDB_read"]["user"],
      passwd=config["mysqlDB_read"]["passwd"],
      database=config["mysqlDB_read"]["database"],
      charset=config["mysqlDB_read"]["charset"]
    )
    
    mycursor1 = mydb1.cursor(pymysql.cursors.DictCursor)
    
    table=config["mysqlDB_read"]["table"]
    lang_id=8
    #today=str(date.today())
    today=str(date.today() - timedelta(days=10))
    from_time=time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple())
    #query1="select * from {0} as t1 where t1.post_id > {1} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video') order by post_gmt".format(table,last_postid,lang_id)
    #query1='''SELECT * FROM {0} AS t1 WHERE t1.post_gmt > {1} AND t1.post_gmt<UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 AND t1.category_id!=2 AND t1.category_id!=3 AND t1.category_id!=4 AND t1.lang_id={2} AND (t1.post_status='published' OR t1.post_status='published1' OR t1.post_status='published2' OR t1.post_status='published3' OR t1.post_status='published4') AND (TYPE='image' OR TYPE='fullimage' OR TYPE='video') ORDER BY post_gmt'''.format(table,last_postid,lang_id)
    query1='''SELECT * FROM {0} AS t1 WHERE t1.post_gmt > {1} AND t1.post_gmt<{3} AND  t1.category_id!=0 AND t1.category_id!=2 AND t1.category_id!=3 AND t1.category_id!=4 AND t1.lang_id={2} AND (t1.post_status='published' OR t1.post_status='published1' OR t1.post_status='published2' OR t1.post_status='published3' OR t1.post_status='published4') AND (TYPE='image' OR TYPE='fullimage' OR TYPE='video') ORDER BY post_gmt'''.format(table,last_post_gmt,lang_id,last_post_gmt+90*60)
    print(query1)
    mycursor1.execute(query1)    
    myresult1 = list(mycursor1.fetchall() )
    mycursor1.close()
    mydb1.close()
    
    print("Number of new posts: ",len(myresult1))
    if len(myresult1)>0:
        mydb = pymysql.connect(
          host=config["mysqlDB_read"]["host"],
          user=config["mysqlDB_read"]["user"],
          passwd=config["mysqlDB_read"]["passwd"],
          database=config["mysqlDB_read"]["database"],
          charset=config["mysqlDB_read"]["charset"]
        )
        
        mycursor = mydb.cursor(pymysql.cursors.DictCursor)
        
        table=config["mysqlDB_read"]["table"]
        lang_id=8
        week=str(date.today() - timedelta(days=40))
        from_time=time.mktime(datetime.strptime(week, "%Y-%m-%d").timetuple())
        #query="select * from {0} as t1 where t1.post_gmt between {1} and {3} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video')".format(table,from_time,lang_id,time.time()-60)
        query="select * from {0} as t1 where t1.post_gmt between {1} and {3} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video')".format(table,from_time,lang_id,last_post_gmt-10)
        print(query)
        mycursor.execute(query)    
        myresult = list(mycursor.fetchall() )
        print(len(myresult))
        mycursor.close()
        mydb.close()
        
       
        posts_matrix=np.zeros((len(myresult), EMBEDDING_DIM))        
        i=0
        for doc in myresult:
            cleaned_desc=clean_text(doc["post_desc"])
            owords=cleaned_desc.split(" ")
            words=[ w  for w in owords if w not in stopwords and w!='']
            posts_matrix[i]=get_sentence_vector(words,MAX_TEXT_LENGTH, EMBEDDING_DIM)
            i=i+1
        for p in myresult1:
            push_postid= p["post_id"]
            input_text= p["post_desc"]
            cleaned_input_text=clean_text(input_text)
            input_owords=cleaned_input_text.split(" ")
            input_words=[ w  for w in input_owords if w not in stopwords and w!='']
            input_text_vector=get_sentence_vector(input_words,MAX_TEXT_LENGTH, EMBEDDING_DIM)
            
            cos_sim_result=cosine_similarity(posts_matrix, input_text_vector.reshape(1, -1))
            top_match=sorted( [(x,i,myresult[i]["post_id"],myresult[i]["post_desc"]) for (i,x) in enumerate(cos_sim_result) if x>0.80],key=lambda a:a[0], reverse=True )#[:3]
            top_match_postids=[tmp[2] for tmp in top_match]
            print(push_postid," match posts are ",top_match_postids)
            
            if len(top_match_postids)>0:
                #client = MongoClient('mongodb://49.156.128.11:27017/')
                client = MongoClient(config['mongo_local']['url'])
                mdb=client[config['mongo_local']['db']]
                user_docs=mdb[config['mongo_local']['table']].aggregate([
                    {"$match":{"postid" : {"$in":top_match_postids}}}
                    ,{"$group":{"_id":"$custid"}}])
                user_docs=list(user_docs)
                if len(user_docs)>0:
                    t0=time.time()
                    #client_103 = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.102:27017/')
                    client_103 = MongoClient(config['mongo_live']['url'])
                    mdb_103=client_103[config['mongo_live']['db']]
                    mydb2 = pymysql.connect(
                      host=config["mysqlDB_read"]["host"],
                      user=config["mysqlDB_read"]["user"],
                      passwd=config["mysqlDB_read"]["passwd"],
                      database=config["mysqlDB_read"]["database"],
                      charset=config["mysqlDB_read"]["charset"]
                    )
                    
                
                    mycursor2 = mydb2.cursor(pymysql.cursors.DictCursor)
                    
                    pnid_table=config["mysqlDB_read"]["pnid_table"]
                    #push_users=[]
                    for doc in user_docs:
                        doc["postid"]=push_postid
                        print(doc)
# =============================================================================
#                         time_doc=mdb_103[config['mongo_local']['table']].find({
#                                 "track_date":str(date.today())
#                                 ,"cust_id":doc["_id"]}).sort("track_time",-1).limit(1)
#                         time_doc=list(time_doc)
#                         if len(time_doc)>0:
#                             last_push_time=time.mktime(datetime.strptime(str(date.today())+" "+list(time_doc)[0]["track_time"], "%Y-%m-%d %H:%M:%S").timetuple())
#                             print(last_push_time)
#                             if time.time()>last_push_time+(60*60):
#                                 query2="select * FROM user_pnids WHERE custid="+str(doc["_id"])
#                                 print(query2)
#                                 mycursor2.execute(query2)    
#                                 myresult2 = list(mycursor2.fetchall() )
#                                 myresult2[0]["push_date"]=str(myresult2[0]["push_date"]) if myresult2[0]["push_date"]!=None else None
#                                 doc.update(myresult2[0])
#                                 del doc["_id"]
#                                 mdb.push_users.insert_one(doc)
#                                 mdb.push_counts.update_one({'_id':push_postid},{'$inc':{'count':1}},upsert=True)
#                                 #push_users.append(doc) 
#                         else:
# =============================================================================
                        query2="select * FROM user_pnids WHERE custid="+str(doc["_id"])
                        print(query2)
                        mycursor2.execute(query2)    
                        myresult2 = list(mycursor2.fetchall() )
                        if len(myresult2)>0:
                            myresult2[0]["push_date"]=str(myresult2[0]["push_date"]) if myresult2[0]["push_date"]!=None else None
                            doc.update(myresult2[0])
                            del doc["_id"]
                            mdb.push_users.insert_one(doc)
                            mdb.push_counts.update_one({'_id':push_postid},{'$inc':{'count':1}},upsert=True)
                            #push_users.append(doc)
                    print(time.time()-t0)
                    mycursor2.close()
                    mydb2.close()
                    #mdb_103.close()
                    client_103.close()
                    
                else:
                    print("Nobody read ",top_match_postids)
                #mdb.close()
                client.close()
            else:
                print("No similar posts found")
        #print("waiting for 60 seconds...")
        #time.sleep(10)
        return myresult1[-1]["post_gmt"]
    else:
        print("No new posts")
        return last_post_gmt
    
    

mydb1 = pymysql.connect(
  host=config["mysqlDB_read"]["host"],
  user=config["mysqlDB_read"]["user"],
  passwd=config["mysqlDB_read"]["passwd"],
  database=config["mysqlDB_read"]["database"],
  charset=config["mysqlDB_read"]["charset"]
)

mycursor1 = mydb1.cursor(pymysql.cursors.DictCursor)

table=config["mysqlDB_read"]["table"]
#today=str(date.today())
today=str(date.today() - timedelta(days=10))
from_time=time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple())
lang_id=8
#query1="select * from {0} as t1 where t1.post_gmt > {1} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video') order by post_id desc limit 1".format(table,from_time,lang_id)
#query1='''SELECT * FROM {0} AS t1 WHERE t1.post_gmt > {1} AND t1.post_gmt<UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND  t1.category_id!=0 AND t1.category_id!=2 AND t1.category_id!=3 AND t1.category_id!=4 AND t1.lang_id={2} AND (t1.post_status='published' OR t1.post_status='published1' OR t1.post_status='published2' OR t1.post_status='published3' OR t1.post_status='published4') AND (TYPE='image' OR TYPE='fullimage' OR TYPE='video') ORDER BY post_gmt desc limit 1'''.format(table,from_time,lang_id)
query1='''SELECT * FROM {0} AS t1 WHERE t1.post_gmt > {1} AND t1.post_gmt<{3} AND  t1.category_id!=0 AND t1.category_id!=2 AND t1.category_id!=3 AND t1.category_id!=4 AND t1.lang_id={2} AND (t1.post_status='published' OR t1.post_status='published1' OR t1.post_status='published2' OR t1.post_status='published3' OR t1.post_status='published4') AND (TYPE='image' OR TYPE='fullimage' OR TYPE='video') ORDER BY post_gmt desc limit 1'''.format(table,from_time,lang_id,from_time+12*60*60)
print(query1)
mycursor1.execute(query1)    
myresult1 = list(mycursor1.fetchall() )
mycursor1.close()
mydb1.close()

last_postid=myresult1[0]["post_gmt"]

#last_postid=3446218

#last_postid=prepare_push_users(last_postid)

while True:
    try:
        last_postid=prepare_push_users(last_postid)
    except Exception as e:
        print("Exception:: ",e)
    print("waiting for 10 seconds...")
    time.sleep(10)


