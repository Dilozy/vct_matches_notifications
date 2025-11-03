#!/bin/sh

/bin/bash docker/wait-for-it.sh postgres:5432 --timeout=60 --strict --

poetry run python src/app/init_db.py

poetry run python src/app/main.py