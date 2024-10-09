import json
from io import BytesIO
from minio import Minio
from config.minio_config import *
from loguru import logger

def init_minio_client():
    minio_client = Minio(
        endpoint,  
        access_key=access_key,
        secret_key=secret_key,
        secure=False 
    )

    return minio_client

def write_json_to_minio(minio_client: Minio, bucket_name: str, object_name: str, data: dict):
    """
    Writes a JSON object to a MinIO bucket.

    :param minio_client: Minio client object.
    :param bucket_name: The bucket name in MinIO where the JSON will be stored.
    :param object_name: The name of the object (file) in the bucket.
    :param data: The dictionary to be stored as a JSON object.
    """
    try:
        # Log start of data conversion
        logger.info("Converting dictionary data to JSON and encoding to bytes.")

        # Convert the dictionary data to a JSON string and encode it to bytes
        json_data = json.dumps(data).encode('utf-8')

        # Log after conversion and encoding
        logger.info(f"Data successfully converted and encoded to JSON for object {object_name}.")

        # Create an in-memory bytes buffer
        json_file = BytesIO(json_data)

        # Ensure the bucket exists; if not, create it
        logger.info(f"Checking if bucket '{bucket_name}' exists in MinIO.")
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created in MinIO.")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists in MinIO.")

        # Upload the JSON file to the specified bucket
        logger.info(f"Uploading object '{object_name}' to bucket '{bucket_name}' in MinIO.")
        minio_client.put_object(
            bucket_name, 
            object_name, 
            json_file, 
            len(json_data), 
            content_type='application/json'
        )
        
        # Log success
        logger.info(f"Successfully uploaded '{object_name}' to bucket '{bucket_name}' in MinIO.")

    except Exception as e:
        # Log any exceptions
        logger.error(f"Error occurred during upload of '{object_name}' to bucket '{bucket_name}': {e}")
        raise
