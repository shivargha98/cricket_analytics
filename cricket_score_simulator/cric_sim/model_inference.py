import numpy as np
import joblib

loaded_rf_model = joblib.load("/home/shivargha/cricket_analytics/cricket_score_simulator/finalized_rf_model_v3.sav")

def inference_random_forest(numpy_array):

    numpy_array = numpy_array.astype(np.float32)
    prediction = loaded_rf_model.predict(numpy_array)
    return prediction

    