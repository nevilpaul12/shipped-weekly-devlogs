from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()
class DevLogs(Base):

    __tablename__ = "logs"

    #id should be auto incremented and primary key
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    title = Column(String)
    description = Column(String)
    links = Column(MutableList.as_mutable(ARRAY(String)), default=list)
    images = Column(MutableList.as_mutable(ARRAY(String)), default=list)
    takeaway = Column(String)
