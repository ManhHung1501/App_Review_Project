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
   - **Username**: `airflow`
   - **Password**: `airflow`
#### 2. Metabase
URL: http://localhost:3000
Database: PostgreSQL
   - **Username**: `airflow`
   - **Password**: `airflow`
#### 3. PostgreSQL
   - **Host**: `localhost`
   - **Port**: `5432`
   - **Username**: `airflow`
   - **Password**: `airflow`  
#### 4. MinIO
API Access: http://localhost:9000
Web UI: http://localhost:9001
- **Access Key**: `admin`
- **Secret Key**: `admin123`

### Running the DAG

To run the DAG, you need to provide configuration values that include Google App IDs, Apple App IDs, and the country code

#### Configuration Parameters

1. **Google App IDs**: A list of Google Play Store application IDs that you want to scrape reviews for.
2. **Apple App IDs**: A list of Apple App Store application IDs that you want to scrape reviews for.
3. **Country**: A string representing the country code (default is `"vn"` for Vietnam).

#### Triggering the DAG

You can trigger the DAG from the Airflow web UI by following these steps:

1. **Access Airflow**: Go to [http://localhost:8080](http://localhost:8080) and log in with the username and password:
   - **Username**: `airflow`
   - **Password**: `airflow`

2. **Find Your DAG**: Locate the DAG that contains the `scrape_reviews_dag` function in the list of available DAGs.

3. **Trigger the DAG**: Click on the **Trigger DAG w/config** button (or the play icon) next to the DAG name.

4. **Provide Configuration**: In the pop-up window, enter the JSON configuration for the DAG run. Here’s an example of how you can structure the JSON:
   ```json
   {
     "google_app_id": ["com.example.app1", "com.example.app2"],
     "apple_app_id": ["123456789", "987654321"],
     "country": "vn"
   }

### Stopping the Containers
To stop the running containers, use:

```bash
docker compose down
```
This will stop and remove the containers, but the volumes will be preserved.