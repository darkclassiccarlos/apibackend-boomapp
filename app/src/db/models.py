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
    rol_id: Optional[int]

class UserBaseCatalog(BaseModel):
    id: int
    email : str

class UserBaseUpdate(BaseModel):
    fullName : str
    password: str
    rol_id: int 

class RolBase(BaseModel):
    name : str

class FamilyproductsBase(BaseModel):
    family_id : str 
    producto_id : str

class FamilysBase(BaseModel):
    id: Optional[int]
    isactive : bool 
    name : str
    user_id : int

class FamilyCreateBase(BaseModel):
    id: Optional[int]
    isactive: bool
    name: str
    user_id: int

class ProductsBase(BaseModel):
    isactive : bool 
    name : str
    namefile : str
    price : float

class ProductCreate(BaseModel):
    id: Optional[int]
    name: Optional[str]
    namefile: Optional[str]
    price: Optional[float]
    family_ids: list[int]

class CustomOAuth2PasswordRequestForm(BaseModel):
    email: str
    password: str

class emailRequest(BaseModel):
    email: str

class recoveryPassword(BaseModel):
    token: str

class PasswordRecovery(BaseModel):
    users_id: str
    new_password: str

class BusinessSave(BaseModel):
    id: Optional[int]
    name : str
    address : str
    telephone : str
    attributes: Optional[str]
    email : str
    description : str
    category : str
    city : str
    state : str
    country : str
    whatsapp : str
    facebook : str
    instagram : str
    users_id : Optional[int]

class DesignsConfigurations(BaseModel):
    business_id : int
    user_id : int
    main_color : str
    secondary_color : str
    cover_image_filename : str
    logo_filename : str
    button_name : str

class PayloadUploadFile(BaseModel):
    base64: str
    folder: str
    fileName: str

# auth models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

