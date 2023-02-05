import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV






###Read trainable data###
df = pd.read_csv("Final_T20_trainable.csv")
data = df.drop(["outcome"],axis=1)
labels = df["outcome"].values

#############creating numpy array from df data###########
data_arr = np.array(data)
#### Splitting the data to create train and val data####
X_train,X_test,y_train,y_test = train_test_split(data_arr,labels,\
                                test_size=0.35,random_state=42)
################### ###################
print('DATA SHAPES:',X_train.shape,y_train.shape)
print("DATA CREATED")


####creating the Search Grid for Random Search###########

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 1000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 200, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [5,10,20,40,80,150,200]


######## Create the random grid ##########
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split}
#################################

print("RANDOM SEARCH GRID:",random_grid)


#### initiating the random search ####
clf_rf = RandomForestClassifier()
rf_random_search = RandomizedSearchCV(estimator = clf_rf, param_distributions = random_grid,\
            n_iter = 100, cv = 3, verbose=3, random_state=42)

rf_random_search.fit(X_train, y_train)
print("Best Features:",rf_random_search.best_params_)