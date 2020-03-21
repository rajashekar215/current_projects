# -*- coding: utf-8 -*-
from datetime import date, timedelta
import re
import pandas as pd
import MySQLdb
import time 

telugu_stop_words=["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి"]
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
        for w in doc:
            w=re.sub('\s*\d*\s', '', w)
            if re.search('(\r\n|\n|\r|\s|\.$|^\.|^,|,$|^\'|\'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$|^#|#$|^\;|\;$|^\d|\d$|^\*|\*$|^-|-$|^\(|\)$|^\/|\/$)',w):
#                         print("wordddd",w)
                        try:
                            start = re.search('(^[\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*)',w).group()
#                             print("start",start)
                            w = w.replace(start,"")
                        except:
                            pass
                        try:
                            end = re.search('([\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*$)',w).group()
#                             print("end",end)
                            w = w.replace(end, "")
                        except:
                            pass
            else:
                pass
                #print("no special chars",w)
#             print(w)                           
            if w is not "":
                try:
#                     print("word  ",w)
                    middle = re.search('[^\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*([\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]+).*',w).groups()[0]
#                     print("middle  ",middle)
                    w = w.replace(middle," ")
                    w=w.split(" ")
#                     print("split  ",w)
                    if w is not "":
                        new_doc.extend(w)
                except:
                    new_doc.append(w)

        rt_df.append(' '.join(new_doc))
    return rt_df


def jaccard_similarity(x,y):
 
   """ returns the jaccard similarity between two lists """
 
   intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
   union_cardinality = len(set.union(*[set(x), set(y)]))
   return intersection_cardinality/float(union_cardinality)


def similarity_score(mydb,mycursor,posts_list,lang_id,district_id):
    #print(posts_list,lang_id,district_id)
    processed_train_data=[]    
    local_table="ugc_posts_local"
    day_before_yesterday=str(date.today() - timedelta(days=2))
    yesterday=str(date.today() - timedelta(days=1))
    today=str(date.today())
    query="select * from {0} where lang_id = {1}  and district_id={2} and post_text != '' AND post_text IS NOT NULL and post_date in {3} and  (review_postid > 0 or review_postid is null) limit 15000".format(local_table,lang_id,district_id,(yesterday,today))
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
            y=processed_train_data[j].split()
            if lang_id==1:
            	x=[w for w in x if w not in telugu_stop_words]
            	y=[w for w in y if w not in telugu_stop_words]
            sim=jaccard_similarity(x,y)
            if sim>=0.1:
                sim_list.append((j,sim))
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
            	sim_posts=sorted(publish,reverse=True)[0]
            elif len(reject)>0:
            	sim_posts=sorted(reject,reverse=True)[0]
            else:
            	sim_posts=sorted(pending,reverse=True)[0]
            #print("match post::::",sim_posts["post_text"])
            
            j_predicted_output.append({'post':posts_list[i]["post_id"],'review_percentage':round(sim_sort[0][1]*100),'review_postid':sim_posts["post_id"]})
            update_query="UPDATE ugc_posts_local SET review_percentage={0} , review_postid={1} where post_id={2} limit 1".format(round(sim_sort[0][1]*100),sim_posts["post_id"],posts_list[i]['post_id'])
            print(update_query)
            #mycursor.execute(update_query)
            #mydb.commit()
        else:
            j_predicted_output.append({'post':posts_list[i]["post_id"],'review_percentage':0,'review_postid':0})
            update_query="UPDATE ugc_posts_local SET review_postid=1 where post_id={0} limit 1".format(posts_list[i]['post_id'])
            print(update_query)
            #mycursor.execute(update_query)
            #mydb.commit()
        processed_train_data.append(processed_test_data[i])
            
    print("district:::",district_id,"\n",j_predicted_output,len(j_predicted_output))            


def get_similarity():
    lang_id=1
    district_ids=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,19,23,24,26,28,30,33,34,42]
    #district_ids=[42]
    mydb = MySQLdb.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )
    
    mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    
    local_table="ugc_posts_local"
    
    post_date=str(date.today())
    
    for did in district_ids:
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
    wait_minutes=1
    print("all districts completed.\nWaiting for {0} minutes".format(wait_minutes))
    time.sleep(60*wait_minutes) 
    get_similarity()
        
    
    
get_similarity()


