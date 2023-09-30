from typing import Optional, Dict, List
from pydantic import BaseModel

# #Base = declarative_base()
# #class User(Base):
class UserBase(BaseModel):
    user : str
    password : str
    email : str
    picture: Optional[str]
    rol_id: Optional[int]

class RolBase(BaseModel):
    name : str

class FamilyproductsBase(BaseModel):
    family_id : str 
    producto_id : str

class FamilysBase(BaseModel):
    isactive : bool 
    name : str
    user_id : int

class ProductsBase(BaseModel):
    isactive : bool 
    name : str
    namefile : str
    price : float