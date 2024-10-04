# #!/bin/bash

# set -e
# set -u

# function create_user_and_database() {
#   local database=$1
#   echo "  Creating user and database '$database'"
#   psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
#     DO \$\$
#     BEGIN
#         IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$database') THEN
#             CREATE USER $database;
#         END IF;
#     END \$\$;
#     CREATE DATABASE $database;
#     GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
# EOSQL
# }

# if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
#   echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
#   for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
#     create_user_and_database $db
#   done
#   echo "Multiple databases created"
# fi

#!/bin/bash
set -e

psql -U airflow -tc "SELECT 1 FROM pg_database WHERE datname='airflow'" | grep -q 1 || \
    psql -U airflow -c "CREATE DATABASE airflow"

psql -U airflow -tc "SELECT 1 FROM pg_database WHERE datname='metabaseappdb'" | grep -q 1 || \
    psql -U airflow -c "CREATE DATABASE metabaseappdb"
