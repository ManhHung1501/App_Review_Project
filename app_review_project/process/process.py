from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, to_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, TimestampType
from config.minio_config import *
from config.common_config import get_project_directory
from config.db_config import *

def process_reviews():
    project_dir = get_project_directory()
    
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("AppReviewPipeline") \
        .config("spark.debug.maxToStringFields", "2000") \
        .config("spark.jars", f"{project_dir}/libs/postgresql-42.6.2.jar, {project_dir}/libs/hadoop-aws-3.3.1.jar, {project_dir}/libs/aws-java-sdk-bundle-1.11.375.jar" ) \
        .config("spark.hadoop.fs.s3a.access.key", access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
        .config("spark.hadoop.fs.s3a.endpoint", endpoint) \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    # Define Apple App Store schema
    apple_app_schema = StructType([
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

    apple_web_schema = StructType([
        StructField("user_name", StringType(), True),
        StructField("title", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("review", StringType(), True),
        StructField("review_date", TimestampType(), True),
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
    apple_reviews_app = spark.read.json("s3a://app-reviews/appstore/app/*.json", schema = apple_app_schema) \
                        .withColumn("review", col("attributes.review")) \
                        .withColumn("rating", col("attributes.rating")) \
                        .withColumn("user_name", col("attributes.userName")) \
                        .withColumn("review_date", col("attributes.date")) \
                        .withColumn("app_id", col("app_id")) \
                        .select("review", "rating","user_name", "review_date", "app_id")
    
    apple_reviews_web = spark.read.json("s3a://app-reviews/appstore/web/*.json", schema = apple_web_schema) \
                        .withColumn("rating", col("rating").cast(IntegerType())) \
                        .select("review", "rating","user_name", "review_date", "app_id")
   
    apple_reviews_combined = apple_reviews_app.unionByName(apple_reviews_web).cache() \
                            .withColumn("store", lit("apple"))
    
    print('Read apple reviews success')

    # Read Google Play Store reviews
    google_reviews = spark.read.json("s3a://app-reviews/google_play/*.json",schema = google_schema) \
                    .withColumnRenamed("content", "review") \
                    .withColumnRenamed("score", "rating") \
                    .withColumnRenamed("userName", "user_name") \
                    .withColumnRenamed("at", "review_date") \
                    .withColumn("review_date", to_timestamp(col("review_date"), "yyyy-MM-dd HH:mm:ss")) \
                    .withColumn("app_id", col("app_id")) \
                    .withColumn("store", lit("google")) \
                    .select("review", "rating","user_name", "review_date", "app_id", "store").cache()

        
    print('Read goolge reviews success')

    # Combine the two dataframes
    df = apple_reviews_combined.unionByName(google_reviews) \
        .withColumn("review", lower(regexp_replace(col("review"), "[\.,\n!:();']", ""))) \
    
    
    return df


