from airflow import DAG
from datetime import datetime, timedelta
from app_review_project.config.common_config import get_project_directory
from airflow.operators.python_operator import PythonOperator
from app_review_project.utils.db_utils import write_df,create_database,create_schema,pgsql_client
from app_review_project.process.process import process_reviews
from app_review_project.config.db_config import *
import logging

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 1),  # Set this to your desired start date
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# Define DAG
dag =  DAG(
    dag_id='process_dag',
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2024, 10, 1),
    catchup=False,
) 
    
project_dir = get_project_directory()

def run_process_review():
    start = datetime.now()
    logging.info('Begin to process reviews ...')
    df = process_reviews()
    create_database(db_name)
    con = pgsql_client(db_name)
    cursor = con.cursor()
    schema_name = 'reviews'
    create_schema(cursor, schema_name)
    write_df(df,'reviews','all_reviews')
    cursor.close()
    con.close()
    logging.info(f'Process reviews succes in {datetime.now()- start}')

process_reviews_task = PythonOperator(
        dag = dag,
        task_id='process_reviews_task',
        python_callable=run_process_review
    )