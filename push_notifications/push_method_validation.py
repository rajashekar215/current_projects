# -*- coding: utf-8 -*-
import time
from pymongo import MongoClient
import configparser
config = configparser.RawConfigParser()
config.read('push_config.ini')

client = MongoClient(config['mongo_local']['url'])
mdb=client[config['mongo_local']['db']]

def validate():
    print("in function  ")
    docs=list(mdb[config['mongo_local']['push_users']].find({'read_status':{'$exists':False}}).limit(1000))
    print(len(docs))
    if len(docs)>0:
        for doc in docs:
            stat=list(mdb['gujarathi_users_posts_data'].find({'custid':doc['custid'],'postid':doc['postid']}))
            if len(stat)>0:
                mdb[config['mongo_local']['push_users']].update({'custid':doc['custid'],'postid':doc['postid']},{'$set':{'read_status':1}},multi=True)
            else:
                mdb[config['mongo_local']['push_users']].update({'custid':doc['custid'],'postid':doc['postid']},{'$set':{'read_status':0}},multi=True)
    else:
        print("no docs")
        time.sleep(10)
        
        
while True:        
    validate()        
