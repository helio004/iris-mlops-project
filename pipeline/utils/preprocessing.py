import tensorflow_transform as tft

from pipeline.utils import features


def preprocessing_fn(inputs):
  """tf.transform's callback function for preprocessing inputs.

  Args:
    inputs: map from feature keys to raw not-yet-transformed features.

  Returns:
    Map from string feature key to transformed feature operations.
  """
  outputs = {}

  for key in features._FEATURE_KEYS:
    outputs[features._transformed_name(key)] = tft.scale_to_z_score(inputs[key])

  outputs[features._transformed_name(features._LABEL_KEY)] = inputs[features._LABEL_KEY]

  return outputs
