from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
# from  databaseFiles.config import config
from contextlib import contextmanager
import os

try:
    DATABASE_URL = os.environ.get('ODBC_SQL_URL')
    # DATABASE_URL = config.get('ODBC_SQL_URL')
except Exception as e:
    raise e

engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(DATABASE_URL))

sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

@contextmanager
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()