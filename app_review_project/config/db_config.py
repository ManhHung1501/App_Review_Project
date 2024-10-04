from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

# Access environment variables
db_host = os.getenv('PGSQL_HOST')
db_port = os.getenv('PGSQL_PORT')
db_user = os.getenv('PGSQL_USERNAME')
db_password = os.getenv('PGSQL_PASSWORD')
db_name = os.getenv('PGSQL_DB')

