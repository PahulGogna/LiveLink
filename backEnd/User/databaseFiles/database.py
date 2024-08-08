from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

try:
    DATABASE_URL = os.environ.get('ODBC_SQL_URL')
except Exception as e:
    raise e

engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(DATABASE_URL))

sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()