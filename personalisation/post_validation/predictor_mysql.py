# -*- coding: utf-8 -*-

from datetime import date, timedelta
import re
import pandas as pd
import MySQLdb

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
                          
# #             w=re.sub('[^A-Za-z]+', '', w)
# #             if w is not "" and w.lower() not in stop_words:
# #                 new_doc.append(w.lower())
        rt_df.append(' '.join(new_doc))
    return rt_df


def jaccard_similarity(x,y):
 
   """ returns the jaccard similarity between two lists """
 
   intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
   union_cardinality = len(set.union(*[set(x), set(y)]))
   return intersection_cardinality/float(union_cardinality)


def similarity_score(mycursor,posts_list,lang_id,district_id):
    #print(posts_list,lang_id,district_id)
    processed_train_data=[]
# =============================================================================
#     mydb = MySQLdb.connect(
#       host="49.156.128.100",
#       user="way2sms",
#       passwd="waysmsawd#$%@",
#       database="way2app",
#       charset='utf8',
#     )
#     
#     mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
#     
# =============================================================================
# =============================================================================
#     publish_table="mag_posts_home_new"
#     #lang_id=1
#     #district_id=42
#     mag_post_date=str(date.today() - timedelta(days=1))
#     query="select * from {0} where lang_id = {1}  and district_ids={2} and post_desc != '' AND post_desc IS NOT NULL and post_date='{3}' and (post_status='published' or post_status='published1' or post_status='published2' or post_status='published3' or post_status='published4') LIMIT 500000;".format(publish_table,lang_id,district_id,mag_post_date)
#     #print(query)
#     mycursor.execute(query)    
#     mag_posts_result = mycursor.fetchall()
#     #mag_posts=mag_posts_result
#     mag_post_length=len(mag_posts_result)
#     print(len(mag_posts_result))
#     
#     processed_train_data.extend(pre_process(mag_posts_result))
# =============================================================================
    
    local_table="ugc_posts_local"
    #lang_id=1
    #district_id=42
    yesterday=str(date.today() - timedelta(days=1))
    today=str(date.today())
    query="select * from {0} where lang_id = {1}  and district_id={2} and post_text != '' AND post_text IS NOT NULL and post_date in {3} and  (review_postid > 0 or review_postid is null) limit 500000".format(local_table,lang_id,district_id,(yesterday,today))
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
    #         print(x,y)
            sim=jaccard_similarity(x,y)
            if sim>=0.1:
                sim_list.append((j,sim))
        if len(sim_list)>0:
            #print(sim_list)
            sim_sort=sorted(sim_list,key=lambda a:a[1],reverse=True)[0:1]
            sim_post_index=sim_sort[0][0]
            sim_posts=None
            #print("match post",sim_post_index,processed_train_data[sim_post_index])
            if sim_post_index>=ugc_posts_length:
                sim_posts=posts_list[sim_post_index-ugc_posts_length]
            else:
                sim_posts=ugc_posts_result[sim_post_index]
            #print("match post::::",sim_posts["post_text"])
            
            j_predicted_output.append({'post':posts_list[i]["post_id"],'review_percentage':round(sim_sort[0][1]*100),'review_postid':sim_posts["post_id"]})
            update_query="UPDATE ugc_posts_local SET review_percentage="+sim_sort[0][1]+" and review_postid="+sim_posts["post_id"]+" where post_id="+posts_list[i]['post_id']+" limit 1"
            mycursor.execute(update_query)
        else:
            j_predicted_output.append({'post':posts_list[i]["post_id"],'review_percentage':0,'review_postid':0})
            update_query="UPDATE ugc_posts_local SET review_postid=1 where post_id="+posts_list[i]['post_id']+" limit 1"
            mycursor.execute(update_query)
        processed_train_data.append(processed_test_data[i])
            
    print("district:::",district_id,"\n",j_predicted_output,len(j_predicted_output))            


def get_similarity():
    lang_id=1
    #district_ids=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,19,23,24,26,28,30,33,34,42]
    district_ids=[42]
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
        query="select * from {0} where lang_id = {1}  and district_id={2} and post_text != '' AND post_text IS NOT NULL and post_date='{3}'and  review_postid=0 order by post_gmt  limit 50000".format(local_table,lang_id,did,post_date)
        #print(query)
        mycursor.execute(query)    
        posts_result = mycursor.fetchall()
        if len(posts_result)>0:
            similarity_score(mycursor,posts_result,lang_id,did)
        else:
            print("no new posts in district "+did)
    
    #get_similarity()
        
    mycursor.close()
    mydb.close()
    
get_similarity()


