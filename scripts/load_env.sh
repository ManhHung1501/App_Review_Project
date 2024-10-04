#!/bin/bash

# Get the IP address of minio and postgres containers
MINIO_IP=minio
POSTGRES_IP=airflow-postgres-1

# Define the path to your .env file
ENV_FILE="./app_review_project/.env" 

# Write the environment variables to the specified .env file
{
    echo "PGSQL_HOST=${POSTGRES_IP}"
    echo "PGSQL_PORT=5432"
    echo "PGSQL_DB=AppReviewDB"
    echo "PGSQL_USERNAME=airflow"
    echo "PGSQL_PASSWORD=airflow"
    echo ""
    echo "# MinIO"
    echo "ACCESS_KEY=admin"
    echo "SECRET_KEY=admin123"
    echo "MINIO_ENDPOINT=${MINIO_IP}:9000"
} > "$ENV_FILE"

# Optionally, print the contents of the .env file to verify
cat "$ENV_FILE"
