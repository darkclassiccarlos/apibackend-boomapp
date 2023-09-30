from .database      import Base, engine
from sqlalchemy     import Column, Integer, String, ForeignKey, BIGINT, Boolean, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel


class users(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    user = Column(String(255),nullable=False)
    picture = Column(String(255),nullable =False,default=None)
    password = Column(String(255),nullable=True)
    email = Column(String(100), nullable=False)
    rol_id = Column(Integer, nullable=False, default=2)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class rol_user(Base):
    __tablename__ = 'rol_user'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    name =  Column(String(100),nullable=False)

class familyproducts(Base):
    __tablename__ = 'familyproducts'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    family_id =  Column(Integer,nullable=False)
    producto_id =  Column(Integer,nullable=False)

class familys(Base):
    __tablename__ = 'familys'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    isactive =  Column(Boolean, default=True)
    name =  Column(String(255),nullable=False)
    user_id = Column(Integer,nullable=False)

class products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    name =  Column(String(255),nullable=False)
    namefile =  Column(String(255),nullable=False)
    price = Column(Float(precision=2), nullable=False)



Base.metadata.create_all(engine)