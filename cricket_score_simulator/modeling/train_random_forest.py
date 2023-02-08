import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
# importing random forest classifier from assemble module
from sklearn.ensemble import RandomForestClassifier
import joblib
from tqdm import tqdm


###Read trainable data###
df = pd.read_csv("cricket_score_simulator/Final_T20_trainable.csv")


######### omitting out batsman data (does not add value to the dataset for prediction)
data = df.drop(['out_batsman_0' 'out_batsman_1' 'out_batsman_2' 'out_batsman_3'
 'out_batsman_4' 'out_batsman_5' 'out_batsman_6' 'out_batsman_7'
 'out_batsman_8' 'out_batsman_9' 'out_batsman_10' 'out_batsman_11'],axis=1)
data = df.drop(["outcome"],axis=1)
#############################################################
labels = df["outcome"].values

#############creating numpy array from df data###########
data_arr = np.array(data)
#### Splitting the data to create train and val data####
X_train,X_test,y_train,y_test = train_test_split(data_arr,labels,test_size=0.30,random_state=42)
################### ###################


# creating a RF classifier
### best params --> max_depth=67, max_features=auto, min_samples_split=40, n_estimators=500 ###
clf = RandomForestClassifier(n_estimators = 500,max_features = "auto",max_depth=67,min_samples_split=40,verbose=3)  
# Training the model on the training dataset
# fit function is used to train the model using the training sets as parameters
clf.fit(X_train, y_train)

filename = 'finalized_rf_model_v3.sav'
joblib.dump(clf, filename)


###### Prediction Analysis ############
correct_num = 0
for i in tqdm(range(X_test.shape[0])):
        pred,actual = clf.predict(X_test[i].reshape(1,-1)),y_test[i]
        if pred == actual:
                correct_num = correct_num + 1
print("Accuracy:",correct_num/X_test.shape[0])

######## 98% accuracy ##############
