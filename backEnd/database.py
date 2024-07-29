from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config
from contextlib import contextmanager

try:
    # DATABASE_URL = os.environ['POSTGRES_URL']
    DATABASE_URL = config.get('POSTGRES_URL')
    # print(DATABASE_URL)
except Exception as e:
    raise e

engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

@contextmanager
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()