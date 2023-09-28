# from typing import Optional, Dict, List
# from pydantic import BaseModel

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

#Base = declarative_base()

#class User(Base):
class User:
    #__tablename__ = "users"
    def __init__(self, user,password):
        #id = Column(Integer, primary_key=True, index=True)
        #self.user = Column(String, unique=True, index=True)
        self.user = user
        #self.password = Column(String)
        self.password = password

class UserLogin(BaseModel):
    username: str
    password: str