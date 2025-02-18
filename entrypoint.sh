#!/bin/sh

echo "Waiting for database to be available..."
/wait-for-it.sh db:3306 --timeout=30 --strict -- echo "Database is ready."

echo "Initializing DB"

python -m repository.init_db

echo "DB has been initialized"