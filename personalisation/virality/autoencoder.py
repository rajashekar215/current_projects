# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy import stats
import tensorflow as tf
import seaborn as sns
from pylab import rcParams
from sklearn.model_selection import train_test_split
from keras.models import Model, load_model
from keras.layers import Input, Dense
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras import regularizers


data=pd.read_csv('creditcard.csv')

count_classes=pd.value_counts(data['Class'],sort=True)
count_classes.plot(kind = 'bar', rot=0)

frauds = data[data.Class == 1]
normal = data[data.Class == 0]

from sklearn.preprocessing import StandardScaler
dat = data.drop(['Time'], axis=1)
dat['Amount'] = StandardScaler().fit_transform(data['Amount'].values.reshape(-1, 1))


X_train, X_test = train_test_split(dat, test_size=0.2, random_state=RANDOM_SEED)
X_train = X_train[X_train.Class == 0]
X_train = X_train.drop(['Class'], axis=1)
y_test = X_test['Class']
X_test = X_test.drop(['Class'], axis=1)
X_train = X_train.values
X_test = X_test.values
X_train.shape

input_dim = X_train.shape[1]
encoding_dim = 18


import keras
input_layer=Input(shape=(input_dim,))
encoder=Dense(encoding_dim,activation="tanh", 
                activity_regularizer=regularizers.l1(10e-5))(input_layer)
encoder=keras.layers.Dropout(0.3)(encoder)
encoder=Dense(int(encoding_dim/2),activation="selu", 
                activity_regularizer=regularizers.l1(10e-5))(encoder)
encoder=keras.layers.Dropout(0.4)(encoder)
encoder=Dense(int(encoding_dim/4),activation="selu", 
                activity_regularizer=regularizers.l1(10e-5))(encoder)
encoder=keras.layers.Dropout(0.4)(encoder)
decoder = Dense(int(encoding_dim / 4), activation='tanh')(encoder)
decoder = Dense(int(encoding_dim / 2), activation='selu')(encoder)
decoder = Dense(input_dim, activation='selu')(decoder)
autoencoder = Model(inputs=input_layer, outputs=decoder)

nb_epoch = 100
batch_size = 128
adam=keras.optimizers.Adam(lr=0.0001)
autoencoder.compile(optimizer='adam', 
                    loss='mean_squared_error', 
                    metrics=['accuracy'])
history = autoencoder.fit(X_train, X_train,
                    epochs=nb_epoch,
                    batch_size=batch_size,
                    shuffle=True,
                    validation_data=(X_test, X_test),
                    verbose=1).history
                          
                          
plt.plot(history['loss'])
plt.plot(history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right');


predictions = autoencoder.predict(X_test)
mse = np.mean(np.power(X_test - predictions, 2), axis=1)
error_df = pd.DataFrame({'reconstruction_error': mse,
                        'true_class': y_test})
error_df.describe()


from sklearn.metrics import (confusion_matrix, precision_recall_curve, auc,
                             roc_curve, recall_score, classification_report, f1_score,
                             precision_recall_fscore_support)



fpr, tpr, thresholds = roc_curve(error_df.true_class, error_df.reconstruction_error)
roc_auc = auc(fpr, tpr)

plt.title('Receiver Operating Characteristic')
plt.plot(fpr, tpr, label='AUC = %0.4f'% roc_auc)
plt.legend(loc='lower right')
plt.plot([0,1],[0,1],'r--')
plt.xlim([-0.001, 1])
plt.ylim([0, 1.001])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show();


threshold = 2.5

groups = error_df.groupby('true_class')
fig, ax = plt.subplots()

for name, group in groups:
    ax.plot(group.index, group.reconstruction_error, marker='o', ms=3.5, linestyle='',
            label= "Fraud" if name == 1 else "Normal")
ax.hlines(threshold, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
ax.legend()
plt.title("Reconstruction error for different classes")
plt.ylabel("Reconstruction error")
plt.xlabel("Data point index")
plt.show();


y_pred = [1 if e > threshold else 0 for e in error_df.reconstruction_error.values]
conf_matrix = confusion_matrix(error_df.true_class, y_pred)
plt.figure(figsize=(12, 12))
sns.heatmap(conf_matrix, xticklabels=LABELS, yticklabels=LABELS, annot=True, fmt="d");
plt.title("Confusion matrix")
plt.ylabel('True class')
plt.xlabel('Predicted class')
plt.show()                            