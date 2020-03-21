# -*- coding: utf-8 -*-
import numpy as np
import time

t1=time.time()


embeddings_index = {}
with open('cc.gu.300.vec', encoding='utf-8', newline='\n', errors='ignore') as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        embedding = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = embedding
print(len(embeddings_index))
print("total time taken:: ",time.time()-t1)

