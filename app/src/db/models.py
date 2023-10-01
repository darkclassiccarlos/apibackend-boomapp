from typing import Optional, Dict, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body

# #Base = declarative_base()
# #class User(Base):
class UserBase(BaseModel):
    fullName : str
    password : str
    email : str
    picture: Optional[str]
    rol_id: int 

class UserBaseUpdate(BaseModel):
    fullName : str
    email : str
    rol_id: int 

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

class CustomOAuth2PasswordRequestForm(BaseModel):
    email: str
    password: str