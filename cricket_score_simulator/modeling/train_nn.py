import pandas as pd
import numpy as np
import json
from sklearn.utils import class_weight
from tensorflow import keras
from sklearn.model_selection import train_test_split
from keras.models import Model
from keras.layers import Input,Dropout
from keras.layers import Dense,BatchNormalization
from keras.utils import to_categorical
import tensorflow_addons as tfa 

df = pd.read_csv("Final_T20_trainable.csv")

#### dropping outcomes 5,7 because they hardly occur in cricket ###
df.drop(df[df["outcome"]==5].index,inplace=True)
df.drop(df[df["outcome"]==7].index,inplace=True)

###Converting outcome 8 to 5###
df.loc[df["outcome"]==8,"outcome"] = 5
############
######### omitting out batsman data (does not add value to the dataset for prediction)
data = df.drop(['batsman_prop5','batsman_prop7','bowler_prop5', 'bowler_prop7',
    'out_batsman_0' ,'out_batsman_1', 'out_batsman_2', 'out_batsman_3',
    'out_batsman_4', 'out_batsman_5', 'out_batsman_6' ,'out_batsman_7',
    'out_batsman_8' ,'out_batsman_9' ,'out_batsman_10' ,'out_batsman_11',"outcome"],axis=1)

labels = df["outcome"].values
labels_encoded = to_categorical(labels)




data_arr = np.array(data)
X_train,X_test,y_train,y_test = train_test_split(data_arr,labels_encoded,test_size=0.35,random_state=42)
X_test,X_val,y_test,y_val = train_test_split(X_test,y_test,test_size=0.40,random_state=42)

#########getting class weights#############
class_weights = class_weight.compute_class_weight(class_weight = 'balanced',\
                                                 classes = np.unique(labels),\
                                                 y = labels)
####################################
class_weights = dict(zip(np.unique(labels), class_weights))
print(class_weights)

### Normalisation of columns###
min_max_dict = {}
#############################
for col_name in list(data.columns):
    if max(data[col_name]) > 1:
        min_max_dict[col_name] = {"min_val":min(data[col_name]), "max_val":max(data[col_name])}
        data[col_name] = (data[col_name] - min(data[col_name])) / (max(data[col_name] - min(data[col_name])))
    #print(i,x,y)

# Serializing json
json_object = json.dumps(min_max_dict, indent=4)
 
# Writing to sample.json
with open("min_max.json", "w") as outfile:
    outfile.write(json_object)

####################################


print(X_train.shape)
print(X_test.shape)
print(X_val.shape)
print(data_arr[0].shape)
print(labels.shape)


############## Create the Keras Model ###################
input_layer = Input(shape=(96,))
x = Dense(256,activation="relu")(input_layer)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
x = Dense(512,activation="relu")(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
x = Dense(1024,activation="relu")(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
output_layer = Dense(7,activation="softmax")(x)

model = Model(inputs=input_layer, outputs=output_layer)
model.compile(optimizer="adam", loss=keras.losses.CategoricalCrossentropy(), metrics="acc")

f1 = tfa.metrics.F1Score(7,'weighted')

model = Model(inputs=input_layer, outputs=output_layer)
model.compile(optimizer="adam", loss=keras.losses.CategoricalCrossentropy(), metrics=[f1])

########### callbacks #######
my_callbacks = [
    keras.callbacks.ModelCheckpoint(filepath='model_13_02_23_4.h5',monitor="val_f1_score",\
    save_best_only=True,mode="max",verbose=True)
]
########################
#weight_classes = {0:1,1:1,2:}
model.fit(X_train,y_train,batch_size=32,epochs=100,callbacks=my_callbacks,\
        validation_data=(X_test,y_test))