import numpy as np
import joblib
from random import choices

loaded_rf_model = joblib.load("/home/shivargha/cricket_analytics/cricket_score_simulator/finalized_rf_model_v6.sav")

def inference_random_forest(numpy_array):

    prediction = loaded_rf_model.predict(numpy_array)
    return prediction


def inference_rf2(numpy_array):
    
    prediction2 = loaded_rf_model.predict_proba(numpy_array)
    for weights in prediction2:
        outcomes = [0,1,2,3,4,6,8]
        pred = choices(outcomes, weights=weights)[0]
    return pred


    