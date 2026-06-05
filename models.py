from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Delegate(Base):
    __tablename__ = "delegates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String)
    school = Column(String)
    country = Column(String)
    committee = Column(String)