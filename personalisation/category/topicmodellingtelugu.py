

import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

import pandas as pd

data=pd.read_csv("teluguposts1l.csv")
data3=pd.read_csv("teluguposts3m.csv")
data1=pd.read_csv("teluguposts50k.csv")

newdata=pd.concat([data,data1])

newdata=newdata[1:]
newdata=np.array(newdata.iloc[:,0])
data[0]
# Tokenize and lemmatize

data3=data3[150000:150200]
dat.to_csv("testdata.csv",index=False)
data3=np.array(data3.iloc[:,0])
data3[1]
import pandas as pd

stopwords = pd.read_csv('telugu_stop_words', header = None)

import numpy as np
stopwords=np.array(stopwords[0])



pun=[',','*','@','!','.',"'",'%','#',":","?",'>','--','↓',"(",")","<"]
     
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
    return ' '.join(new_doc).replace("\u200c"," ")

q=[]
for i in range(len(newdata)):
    a=clean_text(newdata[i])
    q.append(a)
p=[]
for i in range(len(q)):
  word_tokens = word_tokenize(q[i])
  sentence = [w for w in word_tokens if not w in stopwords]
  words = [word for word in sentence if not word in pun]
  p.append(words)

r=[]
for i in range(len(data3)):
    a=clean_text(data3[i])
    r.append(a)

rk=[]
for i in range(len(r)):
  word_tokens = word_tokenize(r[i])
  sentence = [w for w in word_tokens if not w in stopwords]
  words = [word for word in sentence if not word in pun]
  rk.append(words)


q=p[:145642]
r=p[145642:]
    
dictionary = gensim.corpora.Dictionary(q)

dictionary.filter_extremes(no_below=15, no_above=0.1, keep_n= 100000)


bow_corpus = [dictionary.doc2bow(doc) for doc in p]




lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 55, 
                                   id2word = dictionary,                                    
                                   passes = 10,
                                   workers = 2)



for idx, topic in lda_model.print_topics(-1):
    print("Topic: {} \nWords: {}".format(idx, topic ))
    print("\n")



topics=["Movie","Health","Business/Stocks","General","central news",
        "General","Social media","State news","Movie","State news"
        ,"State news","General","Movie","Business/Mobile","General","Agriculture/projects",
        "Religious","General","Movie","General","State news","Movie",
        "Central news","Research","State news","Crime/Security","Central news","General",
        "Crime/Security","Cricket/Sports","Central news","General",
        "State news","State news","State news","Health","General","General",
        "Central news","Crime/Security","Cricket/sports","Education",
        "Business/Mobile","Crime/Security","State news",
        "State news","General","State news","Agriculture/projects","General",
        "Crime/Security","Education","State news","Movie","General"]









topics=lda_model.print_topics()


model1_topics=['state politics','central politics','sports and stocks','Business','Regional news','health and fitness',
   'Movie news','Crime news']

# Data preprocessing step for the unseen document
bow_vector = [dictionary.doc2bow(doc) for doc in rk]

for index, score in sorted(lda_model[bow_vector[10]], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))
    
    


lda_model_1 =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 12, 
                                   id2word = dictionary,                                    
                                   passes = 10,
                                   workers = 2)

topics1=lda_model_1.print_topics()

model2topics=['Transport','Regionl news','politics','social media','Business'
              ,'Cinema news','National cinema news','Healthfitness','international news',
              'state politcs','stocks and sports','crime news']


for idx, topic in lda_model_1.print_topics(-1):
    print("Topic: {} \nWords: {}".format(idx, topic ))
    print("\n")




for index, score in sorted(lda_model_1[bow_vector[10]], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score,lda_model_1.print_topic(index, 5)))
    
    

lda_model_3 =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 10, 
                                   id2word = dictionary,                                    
                                   passes = 10,
                                   workers = 2)

topics3=lda_model_3.print_topics()

model3topics=['cinemanews','','central news','health and fitness','crime news','business'
             'state politics','sports','social media','central politics']



lda_model_4 =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 15, 
                                   id2word = dictionary,                                    
                                   passes = 10,
                                   workers = 2)

topics4=lda_model_4.print_topics()


model4topics=['stocks','Bank news','cinema news','journal news','business/socialmedia','crime/accident news',
              'cricket','Business/climate','health and fitness/proverbs','central news','social media',
              'law and court','sports','central politics','state politics']




for index, score in sorted(lda_model_4[bow_vector[21]], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score,lda_model_4.print_topic(index, 5)))


fin=sorted(lda_model_4[bow_vector[19]], key=lambda tup: -1*tup[1])

fin2=sorted(lda_model_4[bow_vector[10]], key=lambda tup: -1*tup[1])

re=category(fin)
re1=category(fin2)

def category(fi):
    final=fi
    su=0
    i=0
    for i in range(len(final)):
        z=final[i][1]
        su=su+z
        if su>0.8:
            break
        z=0
    k=[]
    j=0
    while j<=i:
        k.append((final[j][0],final[j][1]))
        j=j+1
 
    result=[]
    for p in range(len(k)):
        result.append((topics[k[p][0]],k[p][1]))
    return result
    
    

z=[]
bow_vector = [dictionary.doc2bow(doc) for doc in rk]
for i in range(len(r)):
    fin=sorted(lda_model[bow_vector[i]], key=lambda tup: -1*tup[1])
    re=category(fin)
    z.append(re)



import pickle


with open('dictionary1.pickle', 'wb') as handle:
    pickle.dump(dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('dictionary1.pickle', 'rb') as handle:
    dictionary = pickle.load(handle)



import pandas as pd
dat=pd.DataFrame()
dat['text']=r
dat['category']= z
    
    
lda_model.save('lda1.model')

from gensim import corpora, models, similarities
lda_model =  models.LdaModel.load('lda1.model')

for index, score in sorted(lda_5[bow_vector[21]], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score,lda_5.print_topic(index, 5)))


fin=sorted(lda_5[bow_vector[19]], key=lambda tup: -1*tup[1])

fin2=sorted(lda_5[bow_vector[10]], key=lambda tup: -1*tup[1])

re=category(fin)
re1=category(fin2)

def category(fi):
    final=fi
    su=0
    i=0
    for i in range(len(final)):
        z=final[i][1]
        su=su+z
        if su>0.9:
            break
        z=0
    k=[]
    j=0
    while j<=i:
        k.append((final[j][0],final[j][1]))
        j=j+1
 
    result=[]
    for p in range(len(k)):
        result.append((topics[k[p][0]],k[p][1]))
    return result
    
    

z=[]
bow_vector = [dictionary.doc2bow(doc) for doc in rk]
for i in range(len(r)):
    fin=sorted(lda_model[bow_vector[i]], key=lambda tup: -1*tup[1])
    re=category(fin)
    z.append(re)

k=sorted(dat.loc[1]["category"], key=lambda tup: -1*tup[1])


from collections import defaultdict     
pp=[]
for i in range(len(dat)):
    jj=dat.loc[i]["category"]
    if len(jj)>1:
        def find(pairs): 
            mapp = defaultdict(list) 
            for x, y in pairs: 
                mapp[x].append(y) 
            return [(x, sum(y)) for x, y in mapp.items()] 
        k=find(jj)
        k=sorted(k, key=lambda tup: -1*tup[1])
        if len(k)>2:
            if k[0][1]+k[1][1]+k[2][1]<0.6:
                cat="General"
            else:
                if k[0][1]+k[1][1]>0.6:
                    if k[0][1]*0.4>k[1][1]:
                        cat=k[0][0]
                    elif k[0][1]>0.3:
                        if k[0][0]=="General":
                            cat="General"
                        else:
                            cat="General" +'/'+k[0][0]
                    else:
                        cat=k[0][0]+'/'+k[1][0]           
        elif len(k)>1:
            if k[0][1]+k[1][1]>0.6:
                    if k[0][1]*0.4>k[1][1]:
                        cat=k[0][0]
                    else:
                        cat=k[0][0]+'/'+k[1][0]
        else:
            cat=k[0][0]
            
    else:
        cat=jj[0][0]
    pp.append(cat)


dat["catnew"]=pp












pp=[]
for i in range(len(dat)):
    jj=dat.loc[i]["category"]
    if len(jj)>1:
        if jj[0][1]+jj[1][1]<0.6:
            cat="General"
        else:
            if jj[0][1]*0.4>jj[1][1]:
                cat=jj[0][0]
            else:
                cat=jj[0][0]+'/'+jj[1][0]
    else:
        cat=jj[0][0]
    pp.append(cat)

dat["catnew"]=pp



categories=list(pd.unique(dat["catnew"]))


zzz=[]
ppp=[]
for i in categories:
    da=dat[dat["catnew"]==i]
    da.index=[i for i in range(len(da))]
    if len(da)>1:
        for j in range(len(da)-1):
            p=len(da)
            for k in range(j+1,p):
                x=da.loc[j]["text"]
                s=" "
                n=s.join(x)
                y=da.loc[k]["text"]
                zzz.append(n)
                ss=" "
                c=ss.join(y)
                ppp.append(c)
        
datanew=pd.DataFrame()
datanew["text1"]=zzz
datanew["text2"]=ppp

datanew.to_csv("textcompare")

newda=pd.read_csv("sim")
