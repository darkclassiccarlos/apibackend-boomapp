from .database      import Base, engine
from sqlalchemy     import Column, Integer, String, ForeignKey, BIGINT, Boolean, Float, DateTime,Text
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
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class familys(Base):
    __tablename__ = 'familys'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    isactive =  Column(Boolean, default=True)
    name =  Column(String(255),nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    family_products = relationship('familyproducts', back_populates='family')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True, unique=True, index = True)
    name =  Column(String(255),nullable=False)
    namefile =  Column(String(255),nullable=False)
    price = Column(Float(precision=2), nullable=False)

    family_products = relationship('familyproducts', back_populates='product')
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    
class passwordRecoveryRequest(Base):
    __tablename__ = 'passwordRecoveryRequest'

    id = Column(Integer, primary_key=True, index=True)
    users_id = Column(Integer)
    token = Column(String(255),nullable = False)
    date_request =  Column(DateTime, default=datetime.utcnow)

class business(Base):
    __tablename__ = "business"  # Reemplaza con el nombre de tu tabla
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    address = Column(String(255))
    telephone = Column(String(20))
    attributes = Column(Text)
    email = Column(String(255))
    description = Column(Text)
    category = Column(String(50))
    subdomain = Column(String(255))
    qrpicture = Column(Text)
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    whatsapp = Column(String(50))
    facebook = Column(String(100))
    instagram = Column(String(100))
    users_id = Column(Integer, ForeignKey("users.id"))

class designsconfigurations(Base):
    __tablename__ = "designs_configurations"  # Reemplaza con el nombre de tu tabla
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    main_color = Column(String(50))
    secondary_color = Column(String(50))
    cover_image_filename = Column(String(255))
    logo_filename = Column(String(255))
    button_name = Column(String(255))


Base.metadata.create_all(engine)