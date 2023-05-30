from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Now we have to tell where is the Postgres database located
# SQLALCHEMY_DB_URL = 'postgresql://<username>:<password>@<ip-address or hostname>/<db_name>'
# SQLALCHEMY_DB_URL = 'postgresql://postgres:test123@localhost/fastapi'
# Now we are using the .env file
SQLALCHEMY_DB_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
engine = create_engine(SQLALCHEMY_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()