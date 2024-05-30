from typing import List

import absl
import tensorflow as tf
from tensorflow import keras
import tensorflow_transform as tft
from tfx import v1 as tfx

from pipeline.utils import features
from tfx_bsl.public import tfxio


def _make_serving_signatures(model,
                            tf_transform_output: tft.TFTransformOutput):
  model.tft_layer = tf_transform_output.transform_features_layer()

  @tf.function(input_signature=[
      tf.TensorSpec(shape=[None], dtype=tf.string, name='examples')
  ])
  def serve_tf_examples_fn(serialized_tf_example):
    raw_feature_spec = tf_transform_output.raw_feature_spec()
    raw_feature_spec.pop(features._LABEL_KEY)
    raw_features = tf.io.parse_example(serialized_tf_example, raw_feature_spec)
    transformed_features = model.tft_layer(raw_features)

    outputs = model(transformed_features)
    return {'outputs': outputs}

  @tf.function(input_signature=[
      tf.TensorSpec(shape=[None], dtype=tf.string, name='examples')
  ])
  def transform_features_fn(serialized_tf_example):
    raw_feature_spec = tf_transform_output.raw_feature_spec()
    raw_features = tf.io.parse_example(serialized_tf_example, raw_feature_spec)
    transformed_features = model.tft_layer(raw_features)
    return transformed_features

  return {
      'serving_default': serve_tf_examples_fn,
      'transform_features': transform_features_fn
  }


def _input_fn(file_pattern: List[str],
             data_accessor: tfx.components.DataAccessor,
             tf_transform_output: tft.TFTransformOutput,
             batch_size: int) -> tf.data.Dataset:
  return data_accessor.tf_dataset_factory(
      file_pattern,
      tfxio.TensorFlowDatasetOptions(
          batch_size=batch_size, label_key=features._transformed_name(features._LABEL_KEY)),
      tf_transform_output.transformed_metadata.schema).repeat()



def _build_keras_model() -> tf.keras.Model:
    inputs = [keras.layers.Input(
        shape=(1,), name=features._transformed_name(f)) for f in features._FEATURE_KEYS]
    d = keras.layers.concatenate(inputs)
    for _ in range(3):
        d = keras.layers.Dense(8, activation='relu')(d)
    output = keras.layers.Dense(3, activation='softmax')(d)

    model = keras.Model(inputs=inputs, outputs=output)
    model.compile(
        optimizer=keras.optimizers.Adam(lr=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=[keras.metrics.SparseCategoricalAccuracy()])

    model.summary(print_fn=absl.logging.info)
    return model


def run_fn(fn_args: tfx.components.FnArgs):
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)

    train_dataset = _input_fn(
        fn_args.train_files,
        fn_args.data_accessor,
        tf_transform_output,
        40
    )

    eval_dataset = _input_fn(
        fn_args.eval_files,
        fn_args.data_accessor,
        tf_transform_output, 
        40
    )

    mirrored_strategy = tf.distribute.MirroredStrategy()
    with mirrored_strategy.scope():
        model = _build_keras_model()

    tensorboard_callback = tf.keras.callbacks.TensorBoard(
      log_dir=fn_args.model_run_dir, update_freq='epoch')

    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        callbacks=[tensorboard_callback]
    )

    signatures = _make_serving_signatures(model, tf_transform_output)

    model.save(fn_args.serving_model_dir, save_format='tf', signatures=signatures)
