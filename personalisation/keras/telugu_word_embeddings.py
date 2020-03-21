# -*- coding: utf-8 -*-
import numpy as np
import time

t1=time.time()


embeddings_index = {}
with open('telugu.vec', encoding='utf-8', newline='\n', errors='ignore') as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        embedding = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = embedding
print(len(embeddings_index))
print("total time taken:: ",time.time()-t1)

# =============================================================================
# from joblib import Parallel, delayed
# from tqdm import tqdm
# 
# embeddings_index = {}
# 
# f = open( 'telugu.vec', 'r+', encoding='utf-8')
# def loading(line):
#     values = line.rstrip().rsplit(' ')
#     word = values[0]
#     coefs = np.asarray(values[1:], dtype='float32')
#     return word, coefs
# 
# embeddings_index = dict(Parallel(n_jobs=8,prefer="threads")(delayed(loading)(line) for line in f))
# #embeddings_index = dict(Parallel(n_jobs=-1)(delayed(loading)(line) for line in f))
# 
# f.close()
# print(len(embeddings_index))
# print("total time taken:: ",time.time()-t1)
# =============================================================================

