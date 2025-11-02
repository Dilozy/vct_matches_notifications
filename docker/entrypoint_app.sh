#!/bin/sh

/bin/bash docker/wait-for-it.sh rabbit:5672 --timeout=60 --strict --

/bin/bash docker/wait-for-it.sh postgres:5432 --timeout=60 --strict --

poetry run python src/init_db_rabbit.py

poetry run python src/main.py