# App Review Crawler Project

This project crawls app reviews from the Google Play Store and Apple App Store, processes the data, and provides visualizations through tools like Airflow, Metabase, and MinIO.

## Prerequisites

Ensure you have Docker installed. You can download and install Docker from [here](https://docs.docker.com/get-docker/).

## Getting Started

Follow these steps to set up the environment:

### Step 1: Clone the Repository

```bash
git clone https://github.com/ManhHung1501/App_Review_Project.git
cd App_Review_Project
```
### Step 2: Build and Run the Docker Containers

Run the following command to build the Docker images and start the containers in detached mode:

```bash
docker compose up -d --build
```
This will start the following services:

Airflow for scheduling DAGs and workflows.
Metabase for visualizing the data.
PostgreSQL for storing data.
MinIO for file storage.
### Accessing the Services
Once the containers are running, you can access the services through the following URLs:

#### 1. Airflow
URL: http://localhost:8080
Username: airflow
Password: airflow
#### 2. Metabase
URL: http://localhost:3000
Database: PostgreSQL
Username: airflow
Password: airflow
#### 3. PostgreSQL
Host: localhost
Port: 5432
Username: airflow
Password: airflow
#### 4. MinIO
API Access: http://localhost:9000
Web UI: http://localhost:9001
Access Key: admin
Secret Key: admin123

### Stopping the Containers
To stop the running containers, use:

```bash
docker compose down
```
This will stop and remove the containers, but the volumes will be preserved.