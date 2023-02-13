from tensorflow.keras.models import load_model
import tensorflow_addons as tfa 
import numpy as np
from random import choices

f1 = tfa.metrics.F1Score(7,'weighted')
model = load_model("/home/shivargha/cricket_analytics/cricket_score_simulator/model_13_02_23_3.h5", 
                    custom_objects={"f1":f1})


def model_inference(numpy_array):

    prediction = model.predict(numpy_array,verbose=0)
    pred_outcome = np.argmax(prediction)
    return pred_outcome



def model_inference2(numpy_array):

    prediction = model.predict(numpy_array,verbose=0)
    for weights in prediction:
        outcomes = [0,1,2,3,4,5,6]
        pred = choices(outcomes, weights=weights)[0]

    return pred
