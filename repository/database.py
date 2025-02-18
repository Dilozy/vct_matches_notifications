from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import get_db_connection_url


engine = create_engine(
    url=get_db_connection_url(),
    pool_size=5,
    max_overflow=10,
)

session_factory = sessionmaker(engine)

class Base(DeclarativeBase):
    pass
