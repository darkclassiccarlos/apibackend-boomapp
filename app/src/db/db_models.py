from .database      import Base, engine
from sqlalchemy     import Column, Integer, String, ForeignKey, BIGINT, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime


class users(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    name = Column(String(255),nullable=False)
    picture = Column(String(255),nullable =True,default=None)
    password = Column(String(255),nullable=True)
    email = Column(String(100), nullable=False)
    rol_id = Column(Integer, default=2)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class roluser(Base):
    __tablename__ = 'roluser'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    name =  Column(String(100),nullable=False)

class familyproducts(Base):
    __tablename__ = 'familyproducts'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    family_id = Column(Integer, ForeignKey('familys.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    # Define la relación con Product
    # Relaciones con 'Family' y 'Product'
    family = relationship('familys', back_populates='family_products')
    product = relationship('products', back_populates='family_products')


class familys(Base):
    __tablename__ = 'familys'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    isactive =  Column(Boolean, default=True)
    name =  Column(String(255),nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    family_products = relationship('familyproducts', back_populates='family')

class products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    name =  Column(String(255),nullable=False)
    namefile =  Column(String(255),nullable=False)
    price = Column(Float(precision=2), nullable=False)

    family_products = relationship('familyproducts', back_populates='product')



class passwordRecoveryRequest(Base):
    __tablename__ = 'passwordRecoveryRequest'

    id = Column(Integer, primary_key=True, index=True)
    users_id = Column(Integer)
    token = Column(String(255),nullable = False)
    date_request =  Column(DateTime, default=datetime.utcnow)



Base.metadata.create_all(engine)