from databaseFiles.database import Base
from sqlalchemy import Column, Integer,String,Sequence,ARRAY, Boolean, ForeignKey

class Users(Base):
    __tablename__ = "users"
    id = Column("id",Integer,Sequence("id sequence",start=1), primary_key=True, nullable=False)
    name = Column("name",String, nullable=False)
    email = Column("email",String, nullable = False)
    password = Column("password",String, nullable= False)

class Link(Base):
    __tablename__ = "links"
    id = Column("id",Integer,Sequence("id sequence",start=1), primary_key=True, nullable=False)
    by = Column("by", Integer, ForeignKey('users.id'), nullable = False)
    url = Column("url", String, nullable = False)
    status_code = Column("status_code", Integer, nullable=False)
    working = Column('working', Boolean, default=True)
    running = Column('running', Boolean, default=False)
    exception = Column('exception', Boolean, default=False)
    error = Column('error', String, nullable=True)