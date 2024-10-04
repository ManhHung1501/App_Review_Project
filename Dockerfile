# Use the official Apache Airflow image
FROM apache/airflow:2.10.2

# Set the working directory
WORKDIR /opt/airflow

# Switch to root user to install packages
USER root

# Install required packages for downloading and extracting JDK
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl tar && \
    rm -rf /var/lib/apt/lists/*

# Download and install OpenJDK 11 from OpenLogic
RUN curl -L -o jdk-11.tar.gz "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.24+8/openlogic-openjdk-11.0.24+8-linux-x64.tar.gz" && \
    mkdir -p /usr/local/java && \
    tar -xzf jdk-11.tar.gz -C /usr/local/java && \
    rm jdk-11.tar.gz

# Set environment variables for Java
ENV JAVA_HOME=/usr/local/java/openlogic-openjdk-11.0.24+8-linux-x64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Download and install Spark
ENV SPARK_VERSION=3.5.3
# COPY app_review_project/libs/spark-${SPARK_VERSION}-bin-hadoop3.tgz /usr/local/

# # Extract Spark and set environment variables
# RUN tar -xvf /usr/local/spark-${SPARK_VERSION}-bin-hadoop3.tgz -C /usr/local/ && \
#     mv /usr/local/spark-${SPARK_VERSION}-bin-hadoop3 /usr/local/spark && \
#     rm /usr/local/spark-${SPARK_VERSION}-bin-hadoop3.tgz

RUN curl -o spark.tgz "https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz" && \
    tar -xvf spark.tgz -C /usr/local/ && \
    mv /usr/local/spark-${SPARK_VERSION}-bin-hadoop3 /usr/local/spark && \
    rm spark.tgz
# Set environment variables for Spark
ENV SPARK_HOME=/usr/local/spark
ENV PATH="$SPARK_HOME/bin:$PATH"

# Copy the Poetry configuration files
COPY app_review_project/pyproject.toml app_review_project/poetry.lock ./

USER airflow

# Install Poetry and Apache Airflow Spark provider
RUN pip install poetry apache-airflow-providers-apache-spark==4.11.0

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install

# Copy the entire app_review_project folder to the Airflow working directory
# COPY app_review_project/ .

# Set environment variables for Airflow
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor

# Set the PYTHONPATH so that Airflow can find your app_review_project modules
ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow/app_review_project"

# Expose Airflow ports (Webserver, Worker, Flower, etc.)
EXPOSE 8080 5555 8793

# Command to start Airflow services
ENTRYPOINT ["/entrypoint"]
CMD ["airflow", "webserver"]
