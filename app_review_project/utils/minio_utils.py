import json
from io import BytesIO
from minio import Minio
from config.minio_config import *

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
    # Convert the dictionary data to a JSON string and encode it to bytes
    json_data = json.dumps(data).encode('utf-8')
    
    # Create an in-memory bytes buffer
    json_file = BytesIO(json_data)
    
    # Ensure the bucket exists; if not, create it
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # Upload the JSON file to the specified bucket
    minio_client.put_object(
        bucket_name, 
        object_name, 
        json_file, 
        len(json_data), 
        content_type='application/json'
    )
    
    print(f"Successfully uploaded {object_name} to bucket {bucket_name} in MinIO.")
