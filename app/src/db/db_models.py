from .database      import Base, engine
from sqlalchemy     import Column, Integer, String, ForeignKey, BIGINT
from sqlalchemy.orm import relationship


class users(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    user = Column(String(255),nullable=False)
    password = Column(String(255),nullable=False)

Base.metadata.create_all(engine)