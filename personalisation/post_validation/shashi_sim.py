# -*- coding: utf-8 -*-
from datetime import date, timedelta
import re

import time

from getVectors import getVectors
#import fasttext
#model = fasttext.load_model("cc.te.300.bin")
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import pymysql
import pandas.io.sql as psql
from datetime import date

telugu_stop_words=["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి", "తెలిపారు","ఆయన","రూ","సందర్భంగా","పాల్గొన్నారు","అన్నారు","న","దీంతో","నిర్వహించారు","ఏర్పాటు","వ","లో","చేయాలని","పేర్కొన్నారు","చేసింది","కోరారు","చేసి","తెలిపింది","ఆమె","చెప్పారు","చేస్తున్నారు","జరిగింది","తర్వాత","వెంటనే","వెల్లడించారు","ఏ","మాత్రమే","కోరుతున్నారు","తెలుస్తోంది","తెలిసిందే","తాను","కు","ఇప్పటికే","ఎలాంటి","నిర్వహించిన","దీనిపై","ఇటీవల","ఇది","చేసే","తీసుకోవాలని","పేర్కొంది","చేపట్టారు","చేస్తున్న","గో","చేసినట్లు","చేయడం","మాత్రం","ఉండగా","ఇక","చేసేందుకు","ఇందులో","చేశాడు","తనకు","ఇచ్చారు","చేస్తామని","ను","ఇచ్చిన","చేస్తూ","జరుగుతున్న","గా","మీ","అలాగే","చేసుకోవాలని","ఇవ్వాలని","చేయగా","తో","తమకు","ఉండాలని","ఉండే","ఇదే","తూ","చేస్తున్నట్లు","వచ్చి","వాటిని","ఇప్పుడు","చేసుకున్నారు","ఉంటే","ఉన్నాయి","చేస్తే","ఉంటుంది","వేసి","అంటూ","చేసుకుంది","ఇలా","తనను","వెళ్లి","అయిన","మాట్లాడుతూ","చేపట్టిన","తెలిపాడు","వస్తున్న","కానుంది","ఉండటంతో","చేసుకున్న","అందించారు","ఇలాంటి","వచ్చింది","అదే","మన","వే","దీన్ని","తీసుకున్నారు","అందులో","కావాలని","అందరూ","ఉన్నాయని","చేయనున్నారు","చేయనున్నట్లు","చేసారు","మాట్లాడారు","అక్కడ","అండ్","ఉ","చేసుకుని","నా","ఉందన్నారు","అందరికీ","చేస్తానని","ఆయనకు","చేస్తోంది","నేను","చేశామని","ఇందుకు","ఇక్కడ","చేస్తామన్నారు","చెబుతున్నారు","దీనిని","ని","అందుకే","ఇప్పటి","చెప్పాడు","మా","వాటి","ఉంటాయని","అంటున్నారు","చేయనుంది","అయింది","అన్న","తేది","ఎన్ని","తమను","అన్నాడు","ఎప్పుడు","చేస్తుండగా","చేసుకున్నాడు","ఎప్పుడూ","చేస్తుందని","చేస్తుంది","చేస్తున్నామని","దాన్ని","చేశామన్నారు","చేస్తున్నాయి","చెప్తున్నారు","ల","ఢీ","అందిస్తామని","చేస్తారని","చేసిందని","అవుతుంది","అందుకు","చేస్తారు","అతను","చేపట్టింది","చేస్తోందని","చేసుకోవచ్చని","చేసుకోవచ్చు","చేయనున్న","మీకు","చేస్తున్నాం","గారు","మండలం","లోని","గారి","లు","గారిని","గారికి","లకు","లోకి","జి","వారిని","చేయుచున్నారు"]


def pre_process(df):
    rt_df=[]
    for row in df:
        #print(row['post_desc'])
        if 'post_desc' in row:
            doc=row['post_desc'].split(" ")
        elif 'post_text' in row:
            doc=row['post_text'].split(" ")
        else:
            doc=row.split(" ")
           
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

        rt_df.append(' '.join(new_doc).replace("\u200c"," "))
    return rt_df


def jaccard_similarity(x,y):
 
   """ returns the jaccard similarity between two lists """
 
   intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
   union_cardinality = len(set.union(*[set(x), set(y)]))
   return intersection_cardinality/float(union_cardinality)

def cosine_similarity(x,y):
    average=[]
    p=[]
    p.append(x)
    p.append(y)
    for i in range(len(p)):
        sent_vec = np.zeros(300)
        cnt_words =0;
        for j in range(len(p[i])):
            k=str(np.array(getVectors(p[i][j],1)[0]))
            if k !="None":
               
                vectors = k.split(" ")
                vectors[0]=vectors[0][2:]
                vectors[-1]=vectors[-1][:-1]
                h = list(map(float, vectors))
                sent_vec += h
                cnt_words += 1
   
        if cnt_words != 0:  
            sent_vec /= cnt_words
        average.append(sent_vec)
    c3= np.count_nonzero(average[0])
    c4 =np.count_nonzero(average[1])
    import sklearn
    from scipy import spatial
    if c3 >1 and c4 > 1:
        result = 1 - spatial.distance.cosine(average[0], average[1])
    else:
        result=0.2
    return result      

def similarity_score(mydb,mycursor,posts_list,lang_id,district_id):
    
    #print(posts_list,lang_id,district_id)
    processed_train_data=[]    
    local_table="ugc_posts_local"
    dby=str(date.today() - timedelta(days=2))
    yesterday=str(date.today() - timedelta(days=1))
    today=str(date.today())
    query="select * from {0} where lang_id = {1}  and district_id={2} and post_text != '' AND post_text IS NOT NULL and post_date in {3} and  (review_postid > 0 or review_postid is null) limit 15000".format(local_table,lang_id,district_id,(yesterday,today,dby))
    print(query)
    mycursor.execute(query)    
    ugc_posts_result = mycursor.fetchall()  
    #ugc_posts=ugc_posts_result
    ugc_posts_length=len(ugc_posts_result)
    print("train length:: ",ugc_posts_length)
   
    processed_train_data.extend(pre_process(ugc_posts_result))

    test_posts_length=len(posts_list)
    print("test length:: ",test_posts_length)
   
    processed_test_data=pre_process(posts_list)
   
    #print(processed_test_data)
    j_predicted_output=[]
    for i in range(len(processed_test_data)):
        #print("----",i,"---",posts_list[i]["post_text"])
        sim_list=[]
        for j in range(len(processed_train_data)):    
            x=processed_test_data[i].split()
            test_mandal=posts_list[i]["mandal_id"]
            train_mandal=None
            if j>=len(ugc_posts_result):
                train_mandal=posts_list[j-len(ugc_posts_result)]["mandal_id"]
            else:
                train_mandal=ugc_posts_result[j]["mandal_id"]
               
            if test_mandal==train_mandal:
                y=processed_train_data[j].split()
           
                if lang_id==1:
                x=[w for w in x if w not in telugu_stop_words]
                y=[w for w in y if w not in telugu_stop_words]
               
                c1 =len(x)
                c2= len(y)
                if c1 >1 and c2>1:
               
                    sim=jaccard_similarity(x,y)
                    csim=cosine_similarity(x,y)
                   
                    if csim >= 0.6 and csim <= 0.85:
                        csim=csim+(sim/5)
                        sim_list.append((j,csim))
                    elif csim > 0.85 and csim <= 0.90:
                        sim_list.append((j,csim))
                    elif csim > 0.90 and csim <0.95 and sim<0.5:
                        csim=csim-(sim/15)
                        sim_list.append((j,csim))
                    elif csim>0.90:
                        sim_list.append((j,csim))
               
        if len(sim_list)>0:
            #print(sim_list)
            sim_sort=sorted(sim_list,key=lambda a:a[1],reverse=True)[0:10]
   
            sim_post_indexes=[i[0] for i in sim_sort if i[1]==sim_sort[0][1]]
            publish=[]
            reject=[]
            pending=[]
            sim_posts=None
            #print("match post",sim_post_index,processed_train_data[sim_post_index])
            for sim_post_index in sim_post_indexes:
            if sim_post_index>=ugc_posts_length:
            post=posts_list[sim_post_index-ugc_posts_length]
            if post['post_status']=='submittolocal':
            publish.append(post)
            elif post['post_status']=='feedback':
            reject.append(post)
            else:
            pending.append(post)
            #sim_posts.append(posts_list[sim_post_index-ugc_posts_length])
            else:
            post=ugc_posts_result[sim_post_index]
            if post['post_status']=='submittolocal':
            publish.append(post)
            elif post['post_status']=='feedback':
            reject.append(post)
            else:
            pending.append(post)
            #sim_posts.append(ugc_posts_result[sim_post_index])
            print("matching: publish:: ",len(publish),"  reject:: ",len(reject),"  pending::",len(pending))
            if len(publish)>0:
            sim_posts=sorted(publish,key = lambda i: i['post_gmt'],reverse=True)[0]
            elif len(reject)>0:
            sim_posts=sorted(reject,key = lambda i: i['post_gmt'],reverse=True)[0]
            else:
            sim_posts=sorted(pending,key = lambda i: i['post_gmt'],reverse=True)[0]
            #print("match post::::",sim_posts["post_text"])
           
            j_predicted_output.append({'post':posts_list[i]["post_id"],'review_percentage':round(sim_sort[0][1]*100),'review_postid':sim_posts["post_id"]})
            print(j_predicted_output)
            ran=round(sim_sort[0][1]*100)
            if ran >90:
                comment="Reject"
            elif ran >=80 and ran<=90:
                comment="Check"
            else:
                comment="Accept"
           
            #update_query="UPDATE ugc_posts_local SET review_percentage={0},review_postid={1},ai_status=1,ai_post_status={3} where post_id={2} limit 1".format(round(sim_sort[0][1]*100),sim_posts["post_id"],posts_list[i]['post_id'],comment)
           # print(update_query)
            #mycursor.execute(update_query)
            #mydb.commit()
        else:
            j_predicted_output.append({'post':posts_list[i]["post_id"],'review_percentage':0,'review_postid':0})
            print(j_predicted_output)
            #update_query="UPDATE ugc_posts_local SET review_postid=1,ai_status=1,ai_post_status="Accept" where post_id={0} limit 1".format(posts_list[i]['post_id'])
            #print(update_query)
            #mycursor.execute(update_query)
            #mydb.commit()
        processed_train_data.append(processed_test_data[i])
           
    print("district:::",district_id,"\n",j_predicted_output,len(j_predicted_output))            


def GET_SIMILARITY(lang_id,post_text):
    mydb = pymysql.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )

   
    mycursor = mydb.cursor(pymysql.cursors.DictCursor)
   
    processed_train_data=[]    
    local_table="mag_posts_home_new"
    dby=str(date.today() - timedelta(days=2))
    yesterday=str(date.today() - timedelta(days=1))
    today=str(date.today())
    #query="select * from {0} where lang_id = {1}  and district_id={2} and post_text != '' AND post_text IS NOT NULL and post_date in {3} and  (review_postid > 0 or review_postid is null) limit 15000".format(local_table,lang_id,district_id,(yesterday,today,dby))
    print(query)
    mycursor.execute(query)    
    mag_posts_result = mycursor.fetchall()  
    #ugc_posts=ugc_posts_result
    mag_posts_result=len(mag_posts_result)
    print("train length:: ",mag_posts_result)
   
    processed_train_data.extend(pre_process(mag_posts_result))

    test_posts_length=len(posts_list)
    print("test length:: ",test_posts_length)
   
    processed_test_data=pre_process(posts_list)
   
    #print(processed_test_data)
    j_predicted_output=[]
    sim_list=[]
    x=post_text.split()
    for j in range(len(processed_train_data)):    
               
        x=[w for w in x if w not in telugu_stop_words]
        y=[w for w in y if w not in telugu_stop_words]
       
        c1 =len(x)
        c2= len(y)
        if c1 >1 and c2>1:
       
            sim=jaccard_similarity(x,y)
            csim=cosine_similarity(x,y)
           
            if csim >= 0.6 and csim <= 0.85:
                csim=csim+(sim/5)
                sim_list.append((j,csim))
            elif csim > 0.85 and csim <= 0.90:
                sim_list.append((j,csim))
            elif csim > 0.90 and csim <0.95 and sim<0.5:
                csim=csim-(sim/15)
                sim_list.append((j,csim))
            elif csim>0.90:
                sim_list.append((j,csim))
               
    if len(sim_list)>0:
        #print(sim_list)
        sim_sort=sorted(sim_list,key=lambda a:a[1],reverse=True)[0:10]
   
        sim_post_indexes=[i[0] for i in sim_sort if i[1]==sim_sort[0][1]]
    
    


def get_similarity(lang_id,post_text):
   
    #lang_id=1
    #district_ids=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,19,22,23,24,26,28,30,31,33,34,42,83,84,139,140,158,159,160,162,25,483,157,161,163,482]
    #district_ids=[42]
 
   
    #for did in district_ids:
       
   
    mydb = pymysql.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )

   
    mycursor = mydb.cursor(pymysql.cursors.DictCursor)
   
    local_table="ugc_posts_local"
   
    post_date=str(date.today())
   
    query="select * from {0} where lang_id = {1}  and district_id={2} and post_text != '' AND post_text IS NOT NULL and post_date='{3}'and  review_postid=0 order by post_gmt  limit 2000".format(local_table,lang_id,did,post_date)
    #print(query)
    mycursor.execute(query)    
    posts_result = mycursor.fetchall()
   
   
    if len(posts_result)>0:
        similarity_score(mydb,mycursor,posts_result,lang_id,did)
    else:
        print("no new posts in district ",did)
    mycursor.close()
    mydb.close()
           

# =============================================================================
#     wait_minutes=0.3
#     print("all districts completed.\nWaiting for {0} minutes".format(wait_minutes))
#     time.sleep(60*wait_minutes)
#     get_similarity()
# =============================================================================
       
       
   
   
get_similarity()

