import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
#nltk.download('punkt')
from nltk.tokenize import word_tokenize 
import pandas as pd


#k=category(" రాజ్‌నాథ్‌సింగ్ ఇంట్లో సమావేశమైన కేంద్రమంత్రులు అమిత్ షా, జితేందర్‌సింగ్ , హర్దీప్ సింగ్ పూరీ.. దేశంలో వరదలు, కాశ్మీర్ అంశంపై చర్చ ")



def clean_text(text):
        line =word_tokenize(text)
        new_doc=[]
        for w in line:
            w=re.sub('\s*\d*\s', '', w)
            if re.search('(\r\n|\n|\r|\s|^☛|☛$|\.$|^\.|^,|,$|^\'|\'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$|^#|#$|^\;|\;$|^\d|\d$|^\*|\*$|^-|-$|^\(|\)$|^\/|\/$)',w):
    #                         print("wordddd",w)
                        try:
                            start = re.search('(^[☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*)',w).group()
    #                             print("start",start)
                            w = w.replace(start,"")
                        except:
                            pass
                        try:
                            end = re.search('([☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*$)',w).group()
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
                    middle = re.search('[^☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*([☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]+).*',w).groups()[0]
    #                     print("middle  ",middle)
                    w = w.replace(middle," ")
                    w=w.split(" ")
    #                     print("split  ",w)
                    if w is not "":
                        new_doc.extend(w)
                except:
                    new_doc.append(w)
        return ' '.join(new_doc)
    




def category(query):
    newdata=[]
    newdata.append(query)
    from gensim import corpora, models, similarities
    lda_model =  models.LdaModel.load('lda1.model')
    
    import pickle
    with open('dictionary1.pickle', 'rb') as handle:
        dictionary = pickle.load(handle)
    
    topics=["Movie","Health","Business/Stocks","Movie","central news",
    "Crime/Security","Social media","State news","Movie","State news"
    ,"State news","Climate","Movie","Technology news","General","Agriculture/projects",
    "Religious","General/Sports","Movie","General","State news","Birthday",
    "Central news","Research","State news","Crime/Security","Central news","General",
    "Crime/Security","Cricket/Sports","Election","General",
    "State news","Environmnet","Central news","Health","General","General",
    "Central news","Crime/Security","Cricket/sports","Education",
    "General","Crime/Security","State news",
    "State news","General/Sports","State news","Agriculture/projects","General",
    "Crime/Security","Education","State news","Movie","Education"]
    
# =============================================================================
#     topics=["Movie","Health","Business Stocks","General","central news",
#         "General","Social media","Central news","Movie","State news"
#         ,"State news","General","Movie","Business Mobile","General","Agriculture projects",
#         "Religious","General","Movie","General","State news","Birthday",
#         "Central news","Research","State news","Crime Security","Central news","General",
#         "Crime Security","Cricket Sports","Central news","General",
#         "State news","State news","State news","Health","General","General",
#         "Central news","Crime Security","Cricket sports","Education",
#         "Business Mobile","Crime Security","State news",
#         "State news","General","State news","Agriculture projects","General",
#         "Crime Security","Education","State news","Movie","General"]
# =============================================================================
    
    stopwords = pd.read_csv('telugu_stop_words', header = None)
    
    stopwords=np.array(stopwords[0])
    pun=[',','*','@','!','.',"'",'%','#',":","?",'>','--','↓',"(",")","<"]
         
    
    
        
    p=[]
    for i in range(len(newdata)):
         a=clean_text(newdata[i])
         word_tokens = word_tokenize(a)
         sentence = [w for w in word_tokens if not w in stopwords]
         words = [word for word in sentence if not word in pun]
         p.append(words)
    
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
    bow_vector = [dictionary.doc2bow(doc) for doc in p]
    for i in range(len(p)):
        fin=sorted(lda_model[bow_vector[i]], key=lambda tup: -1*tup[1])
        re=category(fin)
        z.append(re)
        
    
    
    dat=pd.DataFrame()
    dat['text']=newdata
    dat['category']= z
    
    cat=" "
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
                elif k[0][1]>0.3:
                    
                    if k[0][0]=="General":
                        cat="General"
                    else:
                        cat="General" +'/'+k[0][0]
            else:
                cat=k[0][0]
                
        else:
            cat=jj[0][0]
        pp.append(cat)
    
    
    dat["catnew"]=pp
    return dat["catnew"][0].replace("/"," ").replace("news","")
