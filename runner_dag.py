import os
import datetime

from tfx import v1 as tfx

from pipeline import configs
from pipeline import pipeline

from tfx.orchestration.airflow.airflow_runner import AirflowDAGRunner


_DATA_PATH = os.path.join(os.environ['AIRFLOW_HOME'], 'data')

AIRFLOW_CONFIG = {
    'schedule_interval': None,
    'start_date': datetime.datetime.now()
}

DAG = AirflowDAGRunner(AIRFLOW_CONFIG).run(
    pipeline.create_pipeline(
      pipeline_name=configs.PIPELINE_NAME,
      pipeline_root=configs.PIPELINE_ROOT,
      data_path=_DATA_PATH,
      preprocessing_fn=configs.PREPROCESSING_FN,
      run_fn=configs.RUN_FN,
      train_args=tfx.proto.TrainArgs(num_steps=configs.TRAIN_NUM_STEPS),
      eval_args=tfx.proto.EvalArgs(num_steps=configs.EVAL_NUM_STEPS),
      serving_model_dir=configs.SERVING_MODEL_DIR,
      beam_pipeline_args=configs.BEAM_PIPELINE_ARGS,
      metadata_connection_config=tfx.orchestration.metadata
      .sqlite_metadata_connection_config(configs.METADATA_PATH)))
