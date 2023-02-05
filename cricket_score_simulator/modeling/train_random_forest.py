import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
# importing random forest classifier from assemble module
from sklearn.ensemble import RandomForestClassifier
import joblib


###Read trainable data###
df = pd.read_csv("cricket_score_simulator/Final_T20_trainable.csv")
data = df.drop(["outcome"],axis=1)
labels = df["outcome"].values

#############creating numpy array from df data###########
data_arr = np.array(data)
#### Splitting the data to create train and val data####
X_train,X_test,y_train,y_test = train_test_split(data_arr,labels,test_size=0.35)
X_test,X_val,y_test,y_val =  train_test_split(X_test,y_test,test_size=0.10)
################### ###################




# creating a RF classifier
clf = RandomForestClassifier(n_estimators = 100,verbose=3)  
# Training the model on the training dataset
# fit function is used to train the model using the training sets as parameters
clf.fit(X_train, y_train)

filename = 'finalized_rf_model.sav'
joblib.dump(clf, filename)
