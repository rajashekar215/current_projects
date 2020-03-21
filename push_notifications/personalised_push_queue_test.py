# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import pymysql
from datetime import date, timedelta,datetime
import time
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

from load_word_embeddings import * 

stopwords =["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి", "తెలిపారు","ఆయన","రూ","సందర్భంగా","పాల్గొన్నారు","అన్నారు","న","దీంతో","నిర్వహించారు","ఏర్పాటు","వ","లో","చేయాలని","పేర్కొన్నారు","చేసింది","కోరారు","చేసి","తెలిపింది","ఆమె","చెప్పారు","చేస్తున్నారు","జరిగింది","తర్వాత","వెంటనే","వెల్లడించారు","ఏ","మాత్రమే","కోరుతున్నారు","తెలుస్తోంది","తెలిసిందే","తాను","కు","ఇప్పటికే","ఎలాంటి","నిర్వహించిన","దీనిపై","ఇటీవల","ఇది","చేసే","తీసుకోవాలని","పేర్కొంది","చేపట్టారు","చేస్తున్న","గో","చేసినట్లు","చేయడం","మాత్రం","ఉండగా","ఇక","చేసేందుకు","ఇందులో","చేశాడు","తనకు","ఇచ్చారు","చేస్తామని","ను","ఇచ్చిన","చేస్తూ","జరుగుతున్న","గా","మీ","అలాగే","చేసుకోవాలని","ఇవ్వాలని","చేయగా","తో","తమకు","ఉండాలని","ఉండే","ఇదే","తూ","చేస్తున్నట్లు","వచ్చి","వాటిని","ఇప్పుడు","చేసుకున్నారు","ఉంటే","ఉన్నాయి","చేస్తే","ఉంటుంది","వేసి","అంటూ","చేసుకుంది","ఇలా","తనను","వెళ్లి","అయిన","మాట్లాడుతూ","చేపట్టిన","తెలిపాడు","వస్తున్న","కానుంది","ఉండటంతో","చేసుకున్న","అందించారు","ఇలాంటి","వచ్చింది","అదే","మన","వే","దీన్ని","తీసుకున్నారు","అందులో","కావాలని","అందరూ","ఉన్నాయని","చేయనున్నారు","చేయనున్నట్లు","చేసారు","మాట్లాడారు","అక్కడ","అండ్","ఉ","చేసుకుని","నా","ఉందన్నారు","అందరికీ","చేస్తానని","ఆయనకు","చేస్తోంది","నేను","చేశామని","ఇందుకు","ఇక్కడ","చేస్తామన్నారు","చెబుతున్నారు","దీనిని","ని","అందుకే","ఇప్పటి","చెప్పాడు","మా","వాటి","ఉంటాయని","అంటున్నారు","చేయనుంది","అయింది","అన్న","తేది","ఎన్ని","తమను","అన్నాడు","ఎప్పుడు","చేస్తుండగా","చేసుకున్నాడు","ఎప్పుడూ","చేస్తుందని","చేస్తుంది","చేస్తున్నామని","దాన్ని","చేశామన్నారు","చేస్తున్నాయి","చెప్తున్నారు","ల","ఢీ","అందిస్తామని","చేస్తారని","చేసిందని","అవుతుంది","అందుకు","చేస్తారు","అతను","చేపట్టింది","చేస్తోందని","చేసుకోవచ్చని","చేసుకోవచ్చు","చేయనున్న","మీకు","చేస్తున్నాం","గారు","మండలం","లోని","గారి","లు","గారిని","గారికి","లకు","లోకి","జి","వారిని","చేయుచున్నారు"]
     
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


mydb = pymysql.connect(
  host="49.156.128.100",
  user="way2sms",
  passwd="waysmsawd#$%@",
  database="way2app",
  charset='utf8',
)

mycursor = mydb.cursor(pymysql.cursors.DictCursor)

table="mag_posts_home_new"
lang_id=8
week=str(date.today() - timedelta(days=20))
from_time=time.mktime(datetime.strptime(week, "%Y-%m-%d").timetuple())
query="select * from {0} as t1 where t1.post_gmt between {1} and {3} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video')".format(table,from_time,lang_id,time.time()-3600)
print(query)
mycursor.execute(query)    
myresult = list(mycursor.fetchall() )
mycursor.close()
mydb.close()

EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60
posts_matrix=np.zeros((len(myresult), EMBEDDING_DIM))        
i=0
for doc in myresult:
    cleaned_desc=clean_text(doc["post_desc"])
    owords=cleaned_desc.split(" ")
    words=[ w  for w in owords if w not in stopwords and w!='']
    posts_matrix[i]=get_sentence_vector(words,MAX_TEXT_LENGTH, EMBEDDING_DIM)
    i=i+1
#input_text='वाचकांनो, तुमच्यासाठी गूडन्यूज आहे. आता तुमचे आवडते शॉर्ट न्यूज अॅप Way2 तुमचा, तुमच्या मित्रांचा व नातेवाईकांचा वाढदिवस साजरा करणार आहे. त्यासाठी तुम्हाला वाढदिवसाच्या एक दिवस आधी जन्मतारीख व वाढदिवस असणाऱ्याचा उत्तम फोटो marathiteam@way2online.co.in वर सेंड करायचा आहे. बर्थ डे असणाऱ्याला Way2 वरून शुभेच्छा दिल्या जातील. (चांगला फोटो पाठवा...शेअर करा)'
mydb1 = pymysql.connect(
  host="49.156.128.100",
  user="way2sms",
  passwd="waysmsawd#$%@",
  database="way2app",
  charset='utf8',
)

mycursor1 = mydb1.cursor(pymysql.cursors.DictCursor)

table="mag_posts_home_new"
lang_id=8
today=str(date.today())
from_time=time.mktime(datetime.strptime(week, "%Y-%m-%d").timetuple())
query1="select * from {0} as t1 where t1.post_gmt > {1} AND  t1.category_id!=0 and t1.category_id!=2 and t1.lang_id={2} and (t1.post_status='published' or t1.post_status='published1' or t1.post_status='published2' or t1.post_status='published3' or t1.post_status='published4') and (type='image' or type='fullimage' or type='video') limit 1".format(table,from_time,lang_id)
print(query1)
mycursor1.execute(query1)    
myresult1 = list(mycursor1.fetchall() )
mycursor1.close()
mydb1.close()

push_postid= myresult1[0]["post_id"]
input_text= myresult1[0]["post_desc"]

push_postid= 3446783
input_text="રાધનપુરના વેપારી સાથે બનેલી હનીટ્રેપની ઘટનાનો પોલીસે કર્યો પર્દાફાશ.હારીજ નજીક મહિલાએ રાધનપુર તરફથી આવતા વેપારીની કાર રોકી અને લિફ્ટ માંગી.અને થોડી જ દૂર પહોંચ્યા બાદ મહિલાના સાથીઓ અન્ય કારમાં આવીને વેપારીના મહિલા સાથે અશ્લિલ વિડીયો બનાવીને હનીટ્રેપમાં ફસાવી 50 લાખની માંગણી કરતા 4 આરોપીઓ પોલીસના સકંજામાં આવી ગયા હતા અને પોલીસે ચારેય આરોપીઓને દબોચી લીધા હતા"
cleaned_input_text=clean_text(input_text)
input_owords=cleaned_input_text.split(" ")
input_words=[ w  for w in input_owords if w not in stopwords and w!='']
input_text_vector=get_sentence_vector(input_words,MAX_TEXT_LENGTH, EMBEDDING_DIM)

cos_sim_result=cosine_similarity(posts_matrix, input_text_vector.reshape(1, -1))

#ttop_match=sorted( [(x,i,myresult[i]["post_id"],myresult[i]["post_desc"]) for (i,x) in enumerate(cos_sim_result)], reverse=True )

top_match=sorted( [(x,i,myresult[i]["post_id"],myresult[i]["post_desc"]) for (i,x) in enumerate(cos_sim_result) if x>0.85], reverse=True )[:3]

top_match_postids=[tmp[2] for tmp in top_match]


client_103 = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.102:27017/')
mdb_103=client_103["way2"]


client = MongoClient('mongodb://49.156.128.11:27017/')
mdb=client["way2_push"]

if len(top_match_postids)>0:
    user_docs=mdb["gujarathi_users_posts_data"].aggregate([
        {"$match":{"postid" : {"$in":top_match_postids}}}
        ,{"$group":{"_id":"$custid"}}])
    user_docs=list(user_docs)
    
    t0=time.time()
    mydb2 = pymysql.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )
    

    mycursor2 = mydb2.cursor(pymysql.cursors.DictCursor)
    
    table="user_pnids"
    push_users=[]
    for doc in user_docs:
        doc["postid"]=push_postid
        print(doc)
        time_doc=mdb_103['push_notification_tracking_1_2020'].find({
                "track_date":str(date.today())
                ,"cust_id":doc["_id"]}).sort("track_time",-1).limit(1)
        time_doc=list(time_doc)
        if len(time_doc)>0:
            last_push_time=time.mktime(datetime.strptime(str(date.today())+" "+list(time_doc)[0]["track_time"], "%Y-%m-%d %H:%M:%S").timetuple())
            print(last_push_time)
            if time.time()>last_push_time+(60*60):
                query2="select * FROM user_pnids WHERE custid="+str(doc["_id"])
                print(query2)
                mycursor2.execute(query2)    
                myresult2 = list(mycursor2.fetchall() )
                myresult2[0]["push_date"]=str(myresult2[0]["push_date"]) if myresult2[0]["push_date"]!=None else None
                doc.update(myresult2[0])
                del doc["_id"]
                mdb.push_users.insert(doc)
                push_users.append(doc) 
        else:
            query2="select * FROM user_pnids WHERE custid="+str(doc["_id"])
            print(query2)
            mycursor2.execute(query2)    
            myresult2 = list(mycursor2.fetchall() )
            myresult2[0]["push_date"]=str(myresult2[0]["push_date"]) if myresult2[0]["push_date"]!=None else None
            doc.update(myresult2[0])
            del doc["_id"]
            mdb.push_users.insert(doc)
            push_users.append(doc) 
    mycursor2.close()
    mydb2.close()
    print(time.time()-t0)
else:
    print("No similar posts found")            


