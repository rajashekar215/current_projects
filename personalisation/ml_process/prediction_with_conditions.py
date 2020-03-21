# -*- coding: utf-8 -*-

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


def ordering(mdb,mycursor,myresult,custid,from_time,skip,limit):
    print(skip,limit)
    client_103 = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.103:27017/')
    mdb_103=client_103["way2"]
    #user_rating_collection="user_data_new"
    #user_keyword_collection="newsreg-user-keywords-data"
    posts=[]
    breaking=[]
    push_posts=[]
    predict_posts=[]
    seen_posts=[]
#    t1=time.time()-t0
#    print(t1)
   # t2=time.time()
    x = datetime.datetime.now()
    today_date=str(x).split(" ")[0]
    print('track_posts_cat_'+str(today_date.split("-")[2]).replace("0","")+"_"+str(today_date.split("-")[1]).replace("0","")+"_"+today_date.split("-")[0])
    seen_docs=mdb_103['track_posts_cat_'+str(today_date.split("-")[2]).replace("0","")+"_"+str(today_date.split("-")[1]).replace("0","")+"_"+today_date.split("-")[0]].find({"custid":int(custid)})
    #seen_docs=mdb[user_rating_collection].find({"custid" : int(custid),"date" :{'$in':[today_date]}},{"_id":0,"postid":1})
    sp=[]
    for pid in seen_docs:
        #print(pid)
        sp.append(pid["postid"])
    client_103.close()
   
    current_loop_date=str(datetime.datetime.fromtimestamp(from_time)).split(" ")[0]
    push_query="SELECT post_id FROM push_notifications_queue WHERE lang_id=1 AND  push_date='"+current_loop_date+"'"
    mycursor.execute(push_query)
    push_result = mycursor.fetchall()
    push_ids=[]
    for doc in push_result:
        #print("pushhhh",doc)
        push_ids.append(doc["post_id"])
        
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
            s=''
            if "category_name" in post_doc and post_doc["category_name"]: s=s+cat[post_doc["category_name"]] if post_doc["category_name"] in cat else post_doc["category_name"]
            if "keywords" in post_doc and post_doc["keywords"]: s=s+" "+" ".join(post_doc["keywords"])
            posts.append(s)
            predict_posts.append(row)
    b_ids= [d['postid'] for d in breaking]  
    p_ids=  [d['postid'] for d in push_posts]       
    print(b_ids,p_ids)
    
    break_plus_push=[]
    break_plus_push.extend(breaking)
    break_plus_push.extend(push_posts)
    break_plus_push = sorted(break_plus_push, key=itemgetter('post_gmt'), reverse=True)
    #print(posts)
  #  t3=time.time()-t2
   # print(t3)
   # t4=time.time()
    vectorizer = HashingVectorizer()
    #vectorizer=joblib.load("../models/vect_"+str(custid))
    vect_posts=vectorizer.transform(posts)
    try:
        f = open("../models/"+str(custid),'wb+')
        model=joblib.load(f)
        f.close()
        print("old user  ",custid)
        pred=model.predict(vect_posts)
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
       
        zeros=["daysdiff", "categoryid", "show_button", "postid", "btn_text_lang", "writer_custid", "is_ad", "whatsapp_share_count", "fb_share_count", "imgs_count", "sourceid", "lang", "post_parent"]
        for post_doc in final_array:
            for key in post_doc:
                
                if key in post_doc and post_doc[key] is not None:post_doc[key]=str(post_doc[key]) 
                if key in zeros and not post_doc[key]:
                    post_doc[key]=str(0)
        f_ids=  [d['postid'] for d in final_array]       
        print(f_ids)
        unseen_length=len(break_plus_push)+len(unseen_rated_posts)+len(unseen_unrated_posts)
        print("old user","unseen::",unseen_length,"seen",len(seen_posts),"skip::",skip,"limit::",limit)
# =============================================================================
#         try:
#             if skip and limit:
#                 if unseen_length>0 and len(seen_posts)>0:
#                     r_ids=  [d['postid'] for d in final_array[:limit]]       
#                     print("c1",r_ids)
#                     return final_array[:limit]
#                 else:
#                     r_ids=  [d['postid'] for d in final_array[skip:skip+limit]]       
#                     print("c2",r_ids)
#                     return final_array[skip:skip+limit]
#             elif skip and not limit:
#                 if unseen_length>0 and len(seen_posts)>0:
#                     r_ids=  [d['postid'] for d in final_array[:len(final_array)-len(seen_posts)]]       
#                     print("c3",r_ids)
#                     return final_array[:len(final_array)-len(seen_posts)]
#                 else:
#                     r_ids=  [d['postid'] for d in final_array[skip:]]       
#                     print("c4",r_ids)
#                     return final_array[skip:]
#             elif not skip and limit:
#                 r_ids=  [d['postid'] for d in final_array[:limit]]       
#                 print("c5",r_ids)
#                 return final_array[:limit]
#         except Exception as e:
#             print("2c8",e)
#             return []
# =============================================================================
        try:
            if skip and limit:
                if unseen_length>0 and len(seen_posts)>0:
                    res=[]
                    new=len(final_array)-len(seen_posts)
                    res.extend(final_array[:new])
                    if len(res)>=limit:
                        r_ids=  [d['postid'] for d in res]      
                        print("1c1",r_ids)
                        return res
                    else:
                        res.extend(final_array[new+skip:new+skip+limit])
                        r_ids=  [d['postid'] for d in res]      
                        print("1c2",r_ids)
                        return res
                else:
                    r_ids=  [d['postid'] for d in final_array[skip:skip+limit]]       
                    print("1c3",r_ids)
                    return final_array[skip:skip+limit]
            elif skip and not limit:
                if unseen_length>0 and len(seen_posts)>0:
                    res=[]
                    new=len(final_array)-len(seen_posts)
                    res.extend(final_array[:new])
                    if len(res)>=limit:
                        r_ids=  [d['postid'] for d in res]      
                        print("1c4",r_ids)
                        return res
                    else:
                        res.extend(final_array[new+skip:])
                        r_ids=  [d['postid'] for d in res]      
                        print("1c5",r_ids)
                        return res
                else:
                    r_ids=  [d['postid'] for d in final_array[skip:]]       
                    print("1c6",r_ids)
                    return final_array[skip:]
            elif not skip and limit:
                r_ids=  [d['postid'] for d in final_array[:limit]]       
                print("1c7",r_ids)
                return final_array[:limit]
        except Exception as e:
            print("1c8",e)
            return []
    except:
        print("new user  ",custid)
        unseen_posts=[]
        for p in predict_posts:
            if p["postid"] in sp:
                seen_posts.append(p)
            else:
                unseen_posts.append(p)
        
        final_array=[]
        #final_array.extend(breaking)
        #final_array.extend(push_posts)
        final_array.extend(break_plus_push)
        final_array.extend(unseen_posts)
        final_array.extend(seen_posts)
        
        zeros=["daysdiff", "categoryid", "show_button", "postid", "btn_text_lang", "writer_custid", "is_ad", "whatsapp_share_count", "fb_share_count", "imgs_count", "sourceid", "lang", "post_parent"]
        for post_doc in final_array:
            for key in post_doc:
                
                if key in post_doc and post_doc[key] is not None:post_doc[key]=str(post_doc[key]) 
                if key in zeros and not post_doc[key]:
                    post_doc[key]=str(0)
        f_ids=  [d['postid'] for d in final_array]       
        print(f_ids)
        unseen_length=len(break_plus_push)+len(unseen_posts)
        
# =============================================================================
#         try:
#             if len(unseen_length)>0 and len(seen_posts)>0:
#                 r_ids=  [d['postid'] for d in final_array[len(final_array)-len(seen_posts)]]       
#                 print(r_ids)
#                 return final_array[len(final_array)-len(seen_posts)]
#             else:
#                 r_ids=  [d['postid'] for d in final_array[skip:]]       
#                 print(r_ids)
#                 return final_array[skip:]
#         except Exception as e: 
#             print("exception occured",e)
#             return []
# =============================================================================
        print("new user","unseen::",unseen_length,"seen",len(seen_posts),"skip::",skip,"limit::",limit)
        try:
            if skip and limit:
                if unseen_length>0 and len(seen_posts)>0:
                    res=[]
                    new=len(final_array)-len(seen_posts)
                    res.extend(final_array[:new])
                    if len(res)>=limit:
                        r_ids=  [d['postid'] for d in res]      
                        print("2c1",r_ids)
                        return res
                    else:
                        res.extend(final_array[new+skip:new+skip+limit])
                        r_ids=  [d['postid'] for d in res]      
                        print("2c2",r_ids)
                        return res
                else:
                    r_ids=  [d['postid'] for d in final_array[skip:skip+limit]]       
                    print("2c3",r_ids)
                    return final_array[skip:skip+limit]
            elif skip and not limit:
                if unseen_length>0 and len(seen_posts)>0:
                    res=[]
                    new=len(final_array)-len(seen_posts)
                    res.extend(final_array[:new])
                    if len(res)>=limit:
                        r_ids=  [d['postid'] for d in res]      
                        print("2c4",r_ids)
                        return res
                    else:
                        res.extend(final_array[new+skip:])
                        r_ids=  [d['postid'] for d in res]      
                        print("2c5",r_ids)
                        return res
                else:
                    r_ids=  [d['postid'] for d in final_array[skip:]]       
                    print("2c6",r_ids)
                    return final_array[skip:]
            elif not skip and limit:
                r_ids=  [d['postid'] for d in final_array[:limit]]       
                print("2c7",r_ids)
                return final_array[:limit]
        except Exception as e:
            print("2c8",e)
            return []
        
        
def quering(mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,from_time,to_time):
    
    from_time=str(from_time)
    to_time=str(to_time)
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
    return myresult
    


# =============================================================================
# def recursive2(already_length,from_time,to_time,mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,limit,custid,mdb):
#     print(already_length,from_time,to_time)
#     myresult=quering(mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,from_time,to_time)
#     print(already_length,len(myresult),from_time,to_time)
#     result1=ordering(mdb,mycursor,myresult,custid,from_time,pageid-already_length)
#     if len(result1)>=limit:
#         print("response ---- ",result1[:limit])
#         return result1[:limit]
#     else:
#         to_time=from_time
#         from_time=from_time-86400
#         already_length=already_length+len(result1)
#         result2=recursive(already_length,from_time,to_time,mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,limit-len(myresult),custid,mdb) 
#         result1.extend(result2)
#         print(result1)
#         return result1        
# =============================================================================
       



def recursive(already_length,from_time,to_time,mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,limit,custid,mdb):
    print(already_length,from_time,to_time)
    myresult=quering(mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,from_time,to_time)
    print(already_length,len(myresult),from_time,to_time)
    if already_length+len(myresult)>0:
        if pageid+limit<=already_length+len(myresult):
            res=ordering(mdb,mycursor,myresult,custid,from_time,pageid-already_length,limit)
            print("condition1")
            r_ids=  [d['postid'] for d in res]       
            print(r_ids)
            return res
# =============================================================================
#         elif pageid-already_length<len(myresult) and pageid+limit-already_length>len(myresult):
#             print("condition2")
#             result1=ordering(mdb,mycursor,myresult,custid,from_time,pageid-already_length,0)
#             if len(result1)<limit:
#                 print("condition2_1")
#                 to_time=from_time
#                 from_time=from_time-86400
#                 myresult2=quering(mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,from_time,to_time)
#                 result2=ordering(mdb,mycursor,myresult2,custid,from_time,0,limit-len(result1))
#                 result1.extend(result2)
#                 print(result1)
#                 return result1
#             else:
#                 print("condition2_2",result1[:limit])
#                 return result1[:limit]
# =============================================================================
        else:
           print("condition3")
           result1=ordering(mdb,mycursor,myresult,custid,from_time,pageid-already_length,0)
           if not len(result1)==0 and len(result1)<limit:
                print("condition3_1")
                to_time=from_time
                from_time=from_time-86400
                myresult2=quering(mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,from_time,to_time)
                result2=ordering(mdb,mycursor,myresult2,custid,from_time,0,limit-len(result1))
                result1.extend(result2)
                r_ids=  [d['postid'] for d in result1]       
                print(r_ids)
                return result1
           elif len(result1)>=limit:
               print("condition3_2")
               r_ids=  [d['postid'] for d in result1[:limit]]       
               print(r_ids)
               return result1[:limit]
           else:
                print("condition3_3")
                to_time=from_time
                from_time=from_time-86400
                res=recursive(already_length+len(myresult),from_time,to_time,mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,limit,custid,mdb) 
                r_ids=  [d['postid'] for d in res]       
                print(r_ids)
                return res
    else:
          print("condition4",[])
          return []
    
def predictions(custid,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,limit,currentPostTime):
    pageid=int(pageid)
    limit=int(limit)
    client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
    mdb=client["way2"]
    
    
    mydb = MySQLdb.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )
    
    mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    if currentPostTime=='UNIX_TIMESTAMP(CURRENT_TIMESTAMP)':
        currentPostTime=time.time()
    print(int(currentPostTime))
    today_date=str(datetime.datetime.fromtimestamp(int(currentPostTime))).split(" ")[0]
    from_time=time.mktime(datetime.datetime.strptime(today_date, "%Y-%m-%d").timetuple())
    to_time=currentPostTime
    final_result= recursive(0,from_time,to_time,mycursor,lang_id,categoryid,request_source,userEditions,userMandals,userVillages,singleDistrict,pageid,currentPostTime,limit,custid,mdb)
    mycursor.close()
    mydb.close()
    client.close()
    return final_result
    
    



#pprint(predictions(17511156)[0])
