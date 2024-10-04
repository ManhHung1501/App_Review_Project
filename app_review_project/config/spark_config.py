from pyspark.sql import SparkSession
from .common_config import get_project_directory
import os

os.environ['HADOOP_HOME'] = f'{get_project_directory()}/libs/hadoop-3.3.5'  # Adjust this path to where your Hadoop is located
os.environ['PATH'] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')


def create_spark_session_builder():
    spark = SparkSession.builder \
        .config("spark.local.dir", "/tmp/spark") \
        .config("spark.debug.maxToStringFields", "2000") \
        .config("spark.jars", f"{get_project_directory()}/libs/postgresql-42.6.2.jar") \
        .getOrCreate()
    return spark