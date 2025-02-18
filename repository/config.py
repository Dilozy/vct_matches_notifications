import os


def get_db_connection_url(for_jobs=False):
    db_user = os.getenv("POSTGRES_USER")
    db_pw = os.getenv("POSTGRES_PASSWORD")
    
    if for_jobs:
        db_name = "jobs"
    else:
        db_name = os.getenv("POSTGRES_DB")
    
    if os.getenv("DEBUG") == "True":
        db_host = "localhost"
    else:
        db_host = os.getenv("POSTGRES_HOST")

    return f"postgresql+psycopg2://{db_user}:{db_pw}@{db_host}:5432/{db_name}"
