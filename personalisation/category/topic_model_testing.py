# -*- coding: utf-8 -*-
import gensim
#from gensim.utils import simple_preprocess
#from gensim.parsing.preprocessing import STOPWORDS
#from nltk.stem import WordNetLemmatizer, SnowballStemmer
#from nltk.stem.porter import *
import numpy as np
#import nltk
#nltk.download('punkt')
#from nltk.tokenize import word_tokenize
import pandas as pd
import re
from pprint import pprint
from gensim.models import CoherenceModel
import tqdm

#data=pd.read_csv("teluguposts1l.csv")
#data3=pd.read_csv("teluguposts3m.csv")
#data1=pd.read_csv("teluguposts50k.csv")
data=pd.read_csv("telugu_posts_2019.csv")

stopwords =["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి", "తెలిపారు","ఆయన","రూ","సందర్భంగా","పాల్గొన్నారు","అన్నారు","న","దీంతో","నిర్వహించారు","ఏర్పాటు","వ","లో","చేయాలని","పేర్కొన్నారు","చేసింది","కోరారు","చేసి","తెలిపింది","ఆమె","చెప్పారు","చేస్తున్నారు","జరిగింది","తర్వాత","వెంటనే","వెల్లడించారు","ఏ","మాత్రమే","కోరుతున్నారు","తెలుస్తోంది","తెలిసిందే","తాను","కు","ఇప్పటికే","ఎలాంటి","నిర్వహించిన","దీనిపై","ఇటీవల","ఇది","చేసే","తీసుకోవాలని","పేర్కొంది","చేపట్టారు","చేస్తున్న","గో","చేసినట్లు","చేయడం","మాత్రం","ఉండగా","ఇక","చేసేందుకు","ఇందులో","చేశాడు","తనకు","ఇచ్చారు","చేస్తామని","ను","ఇచ్చిన","చేస్తూ","జరుగుతున్న","గా","మీ","అలాగే","చేసుకోవాలని","ఇవ్వాలని","చేయగా","తో","తమకు","ఉండాలని","ఉండే","ఇదే","తూ","చేస్తున్నట్లు","వచ్చి","వాటిని","ఇప్పుడు","చేసుకున్నారు","ఉంటే","ఉన్నాయి","చేస్తే","ఉంటుంది","వేసి","అంటూ","చేసుకుంది","ఇలా","తనను","వెళ్లి","అయిన","మాట్లాడుతూ","చేపట్టిన","తెలిపాడు","వస్తున్న","కానుంది","ఉండటంతో","చేసుకున్న","అందించారు","ఇలాంటి","వచ్చింది","అదే","మన","వే","దీన్ని","తీసుకున్నారు","అందులో","కావాలని","అందరూ","ఉన్నాయని","చేయనున్నారు","చేయనున్నట్లు","చేసారు","మాట్లాడారు","అక్కడ","అండ్","ఉ","చేసుకుని","నా","ఉందన్నారు","అందరికీ","చేస్తానని","ఆయనకు","చేస్తోంది","నేను","చేశామని","ఇందుకు","ఇక్కడ","చేస్తామన్నారు","చెబుతున్నారు","దీనిని","ని","అందుకే","ఇప్పటి","చెప్పాడు","మా","వాటి","ఉంటాయని","అంటున్నారు","చేయనుంది","అయింది","అన్న","తేది","ఎన్ని","తమను","అన్నాడు","ఎప్పుడు","చేస్తుండగా","చేసుకున్నాడు","ఎప్పుడూ","చేస్తుందని","చేస్తుంది","చేస్తున్నామని","దాన్ని","చేశామన్నారు","చేస్తున్నాయి","చెప్తున్నారు","ల","ఢీ","అందిస్తామని","చేస్తారని","చేసిందని","అవుతుంది","అందుకు","చేస్తారు","అతను","చేపట్టింది","చేస్తోందని","చేసుకోవచ్చని","చేసుకోవచ్చు","చేయనున్న","మీకు","చేస్తున్నాం","గారు","మండలం","లోని","గారి","లు","గారిని","గారికి","లకు","లోకి","జి","వారిని","చేయుచున్నారు"]

#pun=[',','*','@','!','.',"'",'%','#',":","?",'>','--','↓',"(",")","<"]
     
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


data['post_desc']=data['post_desc'].apply(clean_text)

processed_data=[]
for doc in data['post_desc']:
    owords=doc.split(" ")
    words=[ w  for w in owords if w not in stopwords]
    processed_data.append(words)
    
    
  
    
bigram = gensim.models.Phrases(processed_data, min_count=5, threshold=100) # higher threshold fewer phrases.
trigram = gensim.models.Phrases(bigram[processed_data], threshold=100)# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)    


def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]  

processed_bigram_data=make_bigrams(processed_data)

test_data=processed_bigram_data

dictionary = gensim.corpora.Dictionary(test_data)

dictionary.filter_extremes(no_below=15, no_above=0.8, keep_n= 100000)

bow_corpus = [dictionary.doc2bow(doc) for doc in test_data]

# =============================================================================
# # =============================================================================
# # 
# # lda_model =  gensim.models.LdaMulticore(bow_corpus, 
# #                                    num_topics = 100, 
# #                                    id2word = dictionary,                                    
# #                                    passes = 5,
# #                                    workers = 2)
# # =============================================================================
# 
# 
# lda_model = gensim.models.LdaMulticore(corpus=bow_corpus,
#                                        id2word=dictionary,
#                                        num_topics=20, 
#                                        random_state=100,
#                                        chunksize=100,
#                                        passes=10,
#                                        per_word_topics=True)
# 
# 
# # =============================================================================
# # for idx, topic in lda_model.print_topics(-1,30):
# #     print("Topic: {} \nWords: {}".format(idx, topic ))
# #     print("\n")
# # =============================================================================
#     
# # Print the Keyword in the 10 topics
# pprint(lda_model.print_topics())
# doc_lda = lda_model[bow_corpus]    
# 
# # Compute Coherence Score
# coherence_model_lda = CoherenceModel(model=lda_model, texts=test_data, dictionary=dictionary, coherence='c_v')
# coherence_lda = coherence_model_lda.get_coherence()
# print('\nCoherence Score: ', coherence_lda)
# =============================================================================



# supporting function
def compute_coherence_values(corpus, dictionary, k, a, b):
    
    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                           id2word=dictionary,
                                           num_topics=k, 
                                           random_state=100,
                                           chunksize=100,
                                           passes=10,
                                           alpha=a,
                                           eta=b,
                                           per_word_topics=True)
    
    coherence_model_lda = CoherenceModel(model=lda_model, texts=test_data, dictionary=dictionary, coherence='c_v')
    #lda_model.save('lda_{0}_{1}_{2}'.format(k,a,b))

    return coherence_model_lda.get_coherence()

# =============================================================================
# 
# cv = compute_coherence_values(corpus=bow_corpus, dictionary=dictionary, 
#                                                   k=160, a=0.01, b=0.9099999999999999)
# =============================================================================

grid = {}
grid['Validation_Set'] = {}# Topics range
min_topics = 50
max_topics = 101
step_size = 10
topics_range = range(min_topics, max_topics, step_size)# Alpha parameter
alpha = list(np.arange(0.01, 1, 0.3))
alpha.append('symmetric')
alpha.append('asymmetric')# Beta parameter
#beta = list(np.arange(0.01, 1, 0.3))
#beta.append('symmetric')# Validation sets
#alpha=[0.01]
beta=[0.9099999999999999]
num_of_docs = len(bow_corpus)
corpus_sets = [# gensim.utils.ClippedCorpus(bow_corpus, num_of_docs*0.25), 
               # gensim.utils.ClippedCorpus(bow_corpus, num_of_docs*0.5), 
               #gensim.utils.ClippedCorpus(bow_corpus, num_of_docs*0.75), 
               bow_corpus]
corpus_title = [
        #'75% Corpus',
        '100% Corpus']
model_results = {'Validation_Set': [],
                 'Topics': [],
                 'Alpha': [],
                 'Beta': [],
                 'Coherence': []
                }
# Can take a long time to run
if 1 == 1:
    pbar = tqdm.tqdm(total=(len(corpus_sets)*len(topics_range)*len(alpha)*len(beta)))
    
    # iterate through validation corpuses
    for i in range(len(corpus_sets)):
        # iterate through number of topics
        for k in topics_range:
            # iterate through alpha values
            for a in alpha:
                # iterare through beta values
                for b in beta:
                    # get the coherence score for the given parameters
                    cv = compute_coherence_values(corpus=corpus_sets[i], dictionary=dictionary, 
                                                  k=k, a=a, b=b)
                    # Save the model results
                    model_results['Validation_Set'].append(corpus_title[i])
                    model_results['Topics'].append(k)
                    model_results['Alpha'].append(a)
                    model_results['Beta'].append(b)
                    model_results['Coherence'].append(cv)
                    print("Topics:{0}, Alpha:{1}, Beta:{2}, Coherence:{3}".format(k,a,b,cv))
                    pbar.update(1)
    pd.DataFrame(model_results).to_csv('lda_tuning_results_two.csv', index=False)
    pbar.close()
    
    
#model_results_df=pd.DataFrame(model_results)    