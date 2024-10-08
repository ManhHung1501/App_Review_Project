from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from app_review_project.scraper.google_play_scraper import get_google_play_reviews
from app_review_project.scraper.appstore_scraper import get_appstore_reviews_app, get_reviews_appstore_web
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.task_group import TaskGroup


def scrape_google_play_reviews_task(app_id):
    print(f"Scraping Google Play reviews for app_id: {app_id}")
    get_google_play_reviews(app_id)


def scrape_apple_app_store_reviews_task(app_id, country):
    print(f"Scraping App Store reviews for app_id: {app_id}")
    get_appstore_reviews_app(country, app_id)
    get_reviews_appstore_web(country, app_id)


# Fetch DAG run configuration
def scrape_config(**kwargs):
    default_config = {   
        "google_app_id": [
            "vn.funzy.trieuhoansu3q",
            "meow.senoidungso.tamquoc"
        ],
        "apple_app_id": [
            "6504213798",
            "6478906911"
        ],
        "country": "vn"
    }
    config = kwargs.get('dag_run').conf or default_config
    google_app_ids = config.get('google_app_id', [])
    apple_app_ids = config.get('apple_app_id', [])
    country = config.get('country', 'vn')
    # Push values to XCom
    kwargs['ti'].xcom_push(key='google_app_ids', value=google_app_ids)
    kwargs['ti'].xcom_push(key='apple_app_ids', value=apple_app_ids)
    kwargs['ti'].xcom_push(key='country', value=country)


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# Define DAG
with DAG(
    dag_id='scrape_reviews_dag',
    default_args=default_args,
    schedule_interval='0 0 * * *',
    start_date=datetime(2024, 10, 1),
    catchup=False,
) as dag:

    scrape_config_task = PythonOperator(
        task_id='get_scrape_config',
        python_callable=scrape_config,
        provide_context=True,
    )

    # Google Play reviews scraping tasks
    def create_google_tasks(**kwargs):
        ti = kwargs['ti']
        google_app_ids = ti.xcom_pull(task_ids='get_scrape_config', key='google_app_ids')
        for app_id in google_app_ids:
            PythonOperator(
                task_id=f'scrape_google_{app_id}',
                python_callable=scrape_google_play_reviews_task,
                op_args=[app_id],
                dag=dag,
            ).execute(context=kwargs)

    google_scraping_tasks = PythonOperator(
        task_id='google_scraping_tasks',
        python_callable=create_google_tasks,
        provide_context=True,
    )


    def create_apple_tasks(**kwargs):
        ti = kwargs['ti']
        apple_app_ids = ti.xcom_pull(task_ids='get_scrape_config', key='apple_app_ids')
        country = ti.xcom_pull(task_ids='get_scrape_config', key='country')
        for app_id in apple_app_ids:
            PythonOperator(
                task_id=f'scrape_apple_{app_id}',
                python_callable=scrape_apple_app_store_reviews_task,
                op_args=[app_id, country],
                dag=dag,
            ).execute(context=kwargs)

    apple_scraping_tasks = PythonOperator(
        task_id='apple_scraping_tasks',
        python_callable=create_apple_tasks,
        provide_context=True,
    )

    trigger_process_task = TriggerDagRunOperator(
        task_id='trigger_process_task',
        trigger_dag_id='process_dag',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Set the task groups to run in parallel
    scrape_config_task >> [google_scraping_tasks, apple_scraping_tasks] >> trigger_process_task
