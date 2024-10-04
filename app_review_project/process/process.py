from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, TimestampType
from config.minio_config import *
from config.common_config import get_project_directory
from utils.db_utils import write_df,create_database, create_schema, pgsql_client
from config.db_config import *
import time

def process_reviews():
    
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("AppReviewPipeline") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901") \
        .config("spark.debug.maxToStringFields", "2000") \
        .config("spark.jars", f"{get_project_directory()}/libs/postgresql-42.6.2.jar") \
        .config("spark.hadoop.fs.s3a.access.key", access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
        .config("spark.hadoop.fs.s3a.endpoint", endpoint) \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    # Define Apple App Store schema
    apple_schema = StructType([
        StructField("id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("attributes", StructType([
            StructField("date", TimestampType(), True),
            StructField("developerResponse", StructType([
                StructField("id", IntegerType(), True),
                StructField("body", StringType(), True),
                StructField("modified", TimestampType(), True)
            ]), True),
            StructField("review", StringType(), True),
            StructField("rating", IntegerType(), True),
            StructField("isEdited", BooleanType(), True),
            StructField("userName", StringType(), True),
            StructField("title", StringType(), True)
        ]), True),
        StructField("offset", StringType(), True),
        StructField("n_batch", IntegerType(), True),
        StructField("app_id", StringType(), True)
    ])

    # Define Google Play schema
    google_schema = StructType([
        StructField('reviewId', StringType(), True),
        StructField('userName', StringType(), True),
        StructField('userImage', StringType(), True),
        StructField('content', StringType(), True),
        StructField('score', IntegerType(), True),
        StructField('thumbsUpCount', IntegerType(), True),
        StructField('reviewCreatedVersion', StringType(), True),
        StructField('at', StringType(), True), 
        StructField('replyContent', StringType(), True),
        StructField('repliedAt', StringType(), True),  
        StructField('appVersion', StringType(), True),
        StructField('app_id', StringType(), True),
    ])

    # Read Apple App Store reviews
    apple_reviews = spark.read.json("s3a://app-reviews/appstore/*.json", schema = apple_schema)
    
    apple_reviews_clean = apple_reviews \
        .withColumn("review", col("attributes.review")) \
        .withColumn("rating", col("attributes.rating")) \
        .withColumn("user_name", col("attributes.userName")) \
        .withColumn("review_date", col("attributes.date")) \
        .withColumn("app_id", col("app_id")) \
        .select("review", "rating","user_name", "review_date", "app_id")
    print('Read apple reviews success')

    # Read Google Play Store reviews
    google_reviews = spark.read.json("s3a://app-reviews/google_play/*.json",schema = google_schema)

    google_reviews_clean = google_reviews \
        .withColumnRenamed("content", "review") \
        .withColumnRenamed("score", "rating") \
        .withColumnRenamed("userName", "user_name") \
        .withColumnRenamed("at", "review_date") \
        .withColumn("review_date", to_timestamp(col("review_date"), "yyyy-MM-dd HH:mm:ss")) \
        .withColumn("app_id", col("app_id")) \
        .select("review", "rating","user_name", "review_date", "app_id")
    print('Read goolge reviews success')

    # Combine the two dataframes
    df = apple_reviews_clean.unionByName(google_reviews_clean) \
        .withColumn("review", lower(regexp_replace(col("review"), "[\.,\n!:();']", ""))) \
    
    
    return df


