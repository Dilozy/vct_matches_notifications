import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_db_connection_url() -> str:
    db_user = os.getenv("POSTGRES_USER")
    db_pw = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    
    if os.getenv("DEBUG") == "True":
        db_host = "localhost"
    else:
        db_host = os.getenv("POSTGRES_HOST")

    return f"postgresql+psycopg://{db_user}:{db_pw}@{db_host}:5432/{db_name}"


engine = create_engine(
    url=get_db_connection_url(),
    pool_size=5,
    max_overflow=10,
)

session_factory = sessionmaker(engine)
