import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
# importing random forest classifier from assemble module
from sklearn.ensemble import RandomForestClassifier
import joblib
from tqdm import tqdm


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
### best params --> max_depth=67, max_features=auto, min_samples_split=40, n_estimators=500 ###
clf = RandomForestClassifier(n_estimators = 500,max_features = "auto",max_depth=67,min_samples_split=40,verbose=3)  
# Training the model on the training dataset
# fit function is used to train the model using the training sets as parameters
clf.fit(X_train, y_train)

filename = 'finalized_rf_model_v2.sav'
joblib.dump(clf, filename)

correct_num = 0
for i in tqdm(range(X_test.shape[0])):
        pred,actual = clf.predict(X_test[i].reshape(1,-1)),y_test[i]
        if pred == actual:
                correct_num = correct_num + 1
print("Accuracy:",correct_num/X_test.shape[0])

######## 65% accuracy ##############
