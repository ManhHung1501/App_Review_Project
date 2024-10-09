import psycopg2
from psycopg2 import sql
from pyspark.sql import DataFrame
from config.db_config import *
import logging

def pgsql_client(db_name):
    try:
        logging.info(f"Attempting to connect to PostgreSQL database: {db_name} on host: {db_host}:{db_port}")
        
        # Establish connection
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user, 
            password=db_password,  
            host=db_host,  
            port=db_port  
        )
        
        conn.autocommit = True
        logging.info(f"Successfully connected to PostgreSQL database: {db_name}")
        return conn
    
    except psycopg2.DatabaseError as e:
        logging.error(f"Failed to connect to PostgreSQL database: {db_name}. Error: {e}")
        raise

def create_database(db_name: str):
    # Connect to PostgreSQL server (default database is usually 'postgres')
    conn = psycopg2.connect(
        dbname="postgres",
        user=db_user, 
        password=db_password,  
        host=db_host,  
        port=db_port  
    )

    # Disable autocommit to run CREATE DATABASE outside a transaction block
    conn.autocommit = True

    # Create a cursor object
    cursor = conn.cursor()

    # Check if the database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()

    if not exists:
        # Create the AppReviewDB database if it doesn't exist
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        logging.info(f"Database {db_name} created successfully!")
    else:
        logging.info(f"Database {db_name} already exists.")

    # Close the connection and cursor
    cursor.close()
    conn.close()

def create_schema(cursor, schema_name: str):
    # Check if the database exists
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    
    # Close the connection and cursor
    cursor.close()


def check_table_exists(cursor, schema: str, table: str):
    # Query to check if the table exists
    cursor.execute(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = '{schema}' AND table_name = '{table}'
        );
    """)
    exists = cursor.fetchone()[0]
    
    return exists

def delete_with_app_id(cursor, schema: str ,table: str, app_id: str):
    tb_exists = check_table_exists(cursor, schema, table)
    if tb_exists:
        cursor.execute(f"DELETE FROM {schema}.{table} WHERE app_id = '{app_id}'")


def write_df(df: DataFrame, schema: str, table: str):
    df.write.format("jdbc") \
        .option("url", f"jdbc:postgresql://{db_host}:{db_port}/{db_name}") \
        .option("user", db_user) \
        .option("password", db_password) \
        .option("dbtable",f"{schema}.{table}") \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()
    logging.info(f'Successfully write data to table {schema}.{table} in PostgreSQL')