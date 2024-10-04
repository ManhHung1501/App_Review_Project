from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

# Access environment variables
access_key = os.getenv('ACCESS_KEY')
secret_key = os.getenv('SECRET_KEY')
endpoint = os.getenv('MINIO_ENDPOINT')