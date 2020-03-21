# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.cluster import MeanShift
from sklearn.cluster import DBSCAN 
import hdbscan
from sklearn.decomposition import PCA
from sklearn.datasets import fetch_mldata
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
#%matplotlib inline
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import time

text_data=pd.read_csv("telugu_posts_2019.csv")


data=np.loadtxt('input_data_telugu_2019.txt')

pca = PCA(n_components=3)
pca_result = pca.fit_transform(data)

pca_df=pd.DataFrame(pca_result)
pca_df.columns =['p1', 'p2','p3']
#pcd=pca_df.iloc[:10,:]
plt.figure(figsize=(16,10))
sns.scatterplot(
    x="p1", y="p2",
    #hue="y",
    #palette=sns.color_palette("hls", 10),
    data=pca_df,
    #legend="full",
    #alpha=0.3
)


ax = plt.figure(figsize=(16,10)).gca(projection='3d')
ax.scatter(
    xs=pca_df["p1"], 
    ys=pca_df["p2"], 
    zs=pca_df["p3"], 
    #c=df.loc[rndperm,:]["y"], 
    cmap='tab10'
)
ax.set_xlabel('p1')
ax.set_ylabel('p2')
ax.set_zlabel('p3')
plt.show()

time_start = time.time()
tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=250)
tsne_results = tsne.fit_transform(pca_df)
print('t-SNE done! Time elapsed: {} seconds'.format(time.time()-time_start))

#pca_df.plot(kind='scatter', x='p1', y='p2')

tips = sns.load_dataset("tips")
sns.scatterplot(x="pca1", y="pca2", data=pca_df)

test_text_data=text_data
test_data=data

ms_cluster = MeanShift(bandwidth=0.1,cluster_all=False).fit(test_data)
joblib.dump(ms_cluster, "mean_shift_model")

labels=ms_cluster.labels_
print(np.unique(labels))
test_text_data["label"]=pd.Series(labels)
print(test_text_data["label"].value_counts())

#text_label_0=test_text_data[test_text_data["label"]==0]

db_cluster = DBSCAN(eps=0.15, min_samples=10).fit(test_data) 
joblib.dump(db_cluster, "DBSCAN_model")

db_labels=db_cluster.labels_
print(np.unique(db_labels))
test_text_data["db_label"]=pd.Series(db_labels)
print(test_text_data["db_label"].value_counts())

text_db_label_7=test_text_data[test_text_data["db_label"]==7]


#hdb_clusterer = hdbscan.HDBSCAN(min_samples=3, min_cluster_size=100, allow_single_cluster=True).fit(test_data)
hdb_clusterer = hdbscan.HDBSCAN(cluster_selection_method="leaf").fit(test_data)
joblib.dump(hdb_clusterer, "HDBSCAN_model")

hdb_clusterer = joblib.load("HDBSCAN_model_mcs_10")


hdb_labels=hdb_clusterer.labels_
print(np.unique(hdb_labels))
test_text_data["hdb_label"]=pd.Series(hdb_labels)
print(test_text_data["hdb_label"].value_counts())
hdbvc=test_text_data["hdb_label"].value_counts()
test_data=pd.DataFrame(test_data)
test_data["hdb_label"]=pd.Series(hdb_labels)


text_hdb_label_data=test_text_data[test_text_data["hdb_label"]==-1]




level2_hdb_data=test_text_data[test_text_data["hdb_label"].isin([-1,2])]
level2_vec_data=test_data[test_data["hdb_label"].isin([-1,2])]

#hdb_clusterer_level2 = hdbscan.HDBSCAN(min_samples=50, min_cluster_size=50, allow_single_cluster=False,cluster_selection_method="leaf").fit(level2_vec_data[:10000])
hdb_clusterer_level2 = hdbscan.HDBSCAN(cluster_selection_method="leaf").fit(level2_vec_data[:10000])
joblib.dump(hdb_clusterer_level2, "HDBSCAN_model_level2")

hdb_labels_level2=hdb_clusterer_level2.labels_
print(np.unique(hdb_labels_level2))
level2_hdb_data["hdb_label"]=pd.Series(hdb_labels_level2)
print(level2_hdb_data["hdb_label"].value_counts())
hdbvc_level2=level2_hdb_data["hdb_label"].value_counts()
#test_data=pd.DataFrame(test_data)
#test_data["hdb_label"]=pd.Series(hdb_labels)

level2_hdb_label_data=level2_hdb_data[level2_hdb_data["hdb_label"]==11]





