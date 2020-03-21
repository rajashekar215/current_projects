import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.externals import joblib

text_data=pd.read_csv("teluguposts4m.csv")


data=np.loadtxt('cat_input_data_telugu.txt')
#test_data=data[:1000]

kmeans = KMeans(n_clusters=20, random_state=0).fit(data)

labels=kmeans.labels_

#kmeans.predict([[0, 0], [12, 3]])

#kmeans.cluster_centers_

text_data["label"]=pd.Series(labels)


joblib.dump(kmeans, "kmeans_20_label_model")


vec_data=pd.DataFrame(data)

vec_data["label"]=pd.Series(labels)



text_label_0=text_data[text_data["label"]==0]
label_0=vec_data[vec_data["label"]==0].iloc[:,:300]
kmeans_label_0  = KMeans(n_clusters=2, random_state=0).fit(label_0)
text_label_0=text_label_0.reset_index()
text_label_0["label"]=pd.Series(kmeans_label_0.labels_)

text_label_0_0=text_label_0[text_label_0["label"]==0]


text_label_2=text_data[text_data["label"]==2]
label_2=vec_data[vec_data["label"]==2].iloc[:,:300]
kmeans_label_2  = KMeans(n_clusters=10, random_state=0).fit(label_2)
text_label_2=text_label_2.reset_index()
text_label_2["label"]=pd.Series(kmeans_label_2.labels_)

text_label_2_1=text_label_2[text_label_2["label"]==1]



kmeans_10_labels  = KMeans(n_clusters=10, random_state=0).fit(data)

labels_10=kmeans_10_labels.labels_

#kmeans.predict([[0, 0], [12, 3]])

#kmeans.cluster_centers_

text_data["labels_10"]=pd.Series(labels_10)

label10_4=text_data[text_data["labels_10"]==5]

#joblib.dump(kmeans, "kmeans_20_label_model")
#label_3.to_csv("political_news.csv")
#label_4.to_csv("sports.csv")

