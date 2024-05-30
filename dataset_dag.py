import os
import logging
from datetime import datetime
import pandas as pd
from sklearn import datasets
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DATA_PATH = os.environ['DATA_DIR']

def iris_etl(data_path: str, filename: str = 'iris.csv'):
    # load iris dataset from sklearn
    logging.info("Read dataset IRIS from sklearn datasets")
    iris = datasets.load_iris(as_frame=True)

    # mapping iris target with names
    # iris_mapping = {i: t for i, t in enumerate(iris.target_names)}

    # concat and save etl result in a folder
    iris_dataset = pd.concat([iris.data, iris.target], axis=1)
    iris_dataset.columns = map(str.lower, iris_dataset.columns)
    iris_dataset.columns = iris_dataset.columns.str.replace(" ", "_")
    iris_dataset.columns = iris_dataset.columns.str.replace("_(cm)", "", regex=False)
    # iris_dataset['target'] = iris_dataset['target'].map(iris_mapping)
    
    if not os.path.exists(data_path):
        os.mkdir(data_path)

    logging.info(f"Save dataset in {data_path}")
    iris_dataset.sample(frac=1.0, random_state=42).to_csv(
        os.path.join(data_path, filename),
        index=False
    )

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 30),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
    'iris_etl_dag',
    default_args=default_args,
    description='A simple ETL DAG for the Iris dataset',
    schedule_interval='@daily',
    catchup=False,
) as dag:
    
    etl_task = PythonOperator(
        task_id='iris_etl_task',
        python_callable=iris_etl,
        op_kwargs={'data_path': DATA_PATH, 'filename': 'iris.csv'},
    )

    etl_task
