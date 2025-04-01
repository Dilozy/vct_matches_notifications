#!/bin/sh

# Ждем готовности RabbitMQ
/wait-for-it.sh rabbit:5672 --timeout=60 --strict -- echo "RabbitMQ is up!"

# Ждем готовности PostgreSQL
/wait-for-it.sh postgres:5432 --timeout=60 --strict -- echo "PostgreSQL is up!"

python -m src.init_db_rabbit

python -m src.main