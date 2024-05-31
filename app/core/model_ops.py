import os

import tensorflow as tf
import numpy as np


MODEL_PATH = os.environ['MODEL_PATH']

def load_latest_model(model_dir):
    subdirs = [
        d 
        for d in os.listdir(model_dir)
        if os.path.isdir(os.path.join(model_dir, d))
    ]

    version_dirs = [int(d) for d in subdirs if d.isdigit()]
    latest_version = max(version_dirs)
    latest_model_path = os.path.join(model_dir, str(latest_version))
    
    model = tf.keras.models.load_model(latest_model_path)
    
    return model


def transform_data(data, model):
    transformed_data = {
        "sepal_length": np.array([[data.sepal_length]], dtype=np.float32),
        "sepal_width": np.array([[data.sepal_width]], dtype=np.float32),
        "petal_length": np.array([[data.petal_length]], dtype=np.float32),
        "petal_width": np.array([[data.petal_width]], dtype=np.float32)
    }
    return model.tft_layer(transformed_data)


def predict(data):
    model = load_latest_model(MODEL_PATH)

    transformed_data = transform_data(data, model)

    pred = np.array(model(transformed_data))
    predicted_class = np.argmax(pred, axis=-1)[0]

    iris_class = {
        0: "setosa",
        1: "versicolor",
        2: "virginica"
    }
    return iris_class[predicted_class]
