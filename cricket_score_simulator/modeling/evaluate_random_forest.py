import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
# importing random forest classifier from assemble module
from sklearn.ensemble import RandomForestClassifier
import joblib
from tqdm import tqdm


###Read trainable data###
df = pd.read_csv("Final_T20_trainable.csv")
######### omitting out batsman data (does not add value to the dataset for prediction)
data = df.drop(['out_batsman_0' ,'out_batsman_1', 'out_batsman_2', 'out_batsman_3',
 'out_batsman_4' ,'out_batsman_5', 'out_batsman_6' ,'out_batsman_7',
 'out_batsman_8' ,'out_batsman_9' ,'out_batsman_10', 'out_batsman_11',"outcome"],axis=1)
#############################################################
#data = df.drop(["outcome"],axis=1)
labels = df["outcome"].values

del df
#############creating numpy array from df data###########
data_arr = np.array(data)
print("DATA CREATED",data_arr.shape)
#### Splitting the data to create train and val data####
X_train,X_test,y_train,y_test = train_test_split(data_arr,labels,test_size=0.30,random_state=42)
################### ###################


########## load model ########
model_path = "/home/shivargha/cricket_analytics/cricket_score_simulator/finalized_rf_model_v3.sav"
clf_rf = joblib.load(model_path)
###########################


########## getting the label counts #######
count_zeros = y_test.size - np.count_nonzero(y_test)
count_1s = np.count_nonzero(y_test == 1)
count_2s = np.count_nonzero(y_test == 2)
count_3s = np.count_nonzero(y_test == 3)
count_4s = np.count_nonzero(y_test == 4)
count_5s = np.count_nonzero(y_test == 5)
count_6s = np.count_nonzero(y_test == 6)
count_7s = np.count_nonzero(y_test == 7)
count_wickets = np.count_nonzero(y_test == 8)
######################## #######################


correct_pred_dict = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0}

for i in tqdm(range(X_test.shape[0])):
        pred,actual = clf_rf.predict(X_test[i].reshape(1,-1)),y_test[i]
        with open("pred.txt","a") as f:
                f.write(str(pred)+" "+str(actual))
                f.write("\n")
        #print(pred,actual)
        if pred == actual:
                correct_num = correct_num + 1
                if actual == 0:
                        correct_pred_dict[0] =correct_pred_dict[0] + 1

                elif actual == 1:
                        correct_pred_dict[1] =correct_pred_dict[1] + 1

                elif actual == 2:
                        correct_pred_dict[2] =correct_pred_dict[2] + 1

                elif actual == 3:
                        correct_pred_dict[3] =correct_pred_dict[3] + 1

                elif actual == 4:
                        correct_pred_dict[4] =correct_pred_dict[4] + 1

                elif actual == 5:
                        correct_pred_dict[5] =correct_pred_dict[5] + 1

                elif actual == 6:
                        correct_pred_dict[6] =correct_pred_dict[6] + 1

                elif actual == 7:
                        correct_pred_dict[7] =correct_pred_dict[7] + 1

                elif actual == 8:
                        correct_pred_dict[8] =correct_pred_dict[8] + 1
        

######################################################################## 
print("Accuracy Metrics")     
print("Accuracy:",correct_num/X_test.shape[0])
print("Accuracy of 0s:",correct_pred_dict[0]/count_zeros)
print("Accuracy of 1s:",correct_pred_dict[1]/count_1s)
print("Accuracy of 2s:",correct_pred_dict[2]/count_2s)
print("Accuracy of 3s:",correct_pred_dict[3]/count_3s)
print("Accuracy of 4s:",correct_pred_dict[4]/count_4s)
print("Accuracy of 5s:",correct_pred_dict[5]/count_5s)
print("Accuracy of 6s:",correct_pred_dict[6]/count_6s)
print("Accuracy of 7s:",correct_pred_dict[7]/count_7s)
print("Accuracy of Wickets:",correct_pred_dict[8]/count_wickets)
#########################################################################


################################################################
print("Predicted Counts")
print("Predicted number of 0s:{} out of {}".format(correct_pred_dict[0],count_zeros))
print("Predicted number of 1s:{} out of {}".format(correct_pred_dict[1],count_1s))
print("Predicted number of 2s:{} out of {}".format(correct_pred_dict[2],count_2s))
print("Predicted number of 3s:{} out of {}".format(correct_pred_dict[3],count_3s))
print("Predicted number of 4s:{} out of {}".format(correct_pred_dict[4],count_4s))
print("Predicted number of 5s:{} out of {}".format(correct_pred_dict[5],count_5s))
print("Predicted number of 6s:{} out of {}".format(correct_pred_dict[6],count_6s))
print("Predicted number of 7s:{} out of {}".format(correct_pred_dict[7],count_7s))
print("Predicted number of wickets:{} out of {}".format(correct_pred_dict[8],count_wickets))
################################################################



# Accuracy Metrics                                                                                                      
# Accuracy: 0.6004198329065032
# Accuracy of 0s: 0.6933867735470942
# Accuracy of 1s: 0.7671437881677086
# Accuracy of 2s: 0.22678260869565217
# Accuracy of 3s: 0.15875613747954173
# Accuracy of 4s: 0.3182916307161346
# Accuracy of 5s: 0.09523809523809523
# Accuracy of 6s: 0.27470075065936295
# Accuracy of 7s: 0.0
# Accuracy of Wickets: 0.17608024691358024
# Predicted Counts
# Predicted number of 0s:31486 out of 45409
# Predicted number of 1s:31782 out of 41429
# Predicted number of 2s:1956 out of 8625
# Predicted number of 3s:97 out of 611
# Predicted number of 4s:3689 out of 11590
# Predicted number of 5s:2 out of 21
# Predicted number of 6s:1354 out of 4929
# Predicted number of 7s:0 out of 1
# Predicted number of wickets:1141 out of 6480