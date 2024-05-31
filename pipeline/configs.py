import os

# Nome do pipeline
PIPELINE_NAME = 'iris_pipeline'

# Funções de treinamento e pré processamento
PREPROCESSING_FN = 'pipeline.utils.preprocessing.preprocessing_fn'
RUN_FN = 'pipeline.utils.train.run_fn'

# Número de etapas de treinamento e de avaliação
TRAIN_NUM_STEPS = 1000
EVAL_NUM_STEPS = 150

# Diretorios de saida dos resultados do pipeline
OUTPUT_DIR = '.'

PIPELINE_ROOT = os.path.join(
  OUTPUT_DIR, 'tfx_pipeline_output', PIPELINE_NAME
)
METADATA_PATH = os.path.join(
  OUTPUT_DIR, 'tfx_metadata', PIPELINE_NAME, 'metadata.db'
)

SERVING_MODEL_DIR = os.environ['SERVING_DIR']

# Argumentos do Beam para o pipeline
BEAM_PIPELINE_ARGS = [
    '--direct_running_mode=multi_processing',
    '--direct_num_workers=0',
]
