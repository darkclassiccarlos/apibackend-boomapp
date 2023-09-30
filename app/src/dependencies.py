# Script para funciones auxiliares
# user_functions.py

from typing import Dict, Optional
import mysql.connector
#from .models import User,UserLogin
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .db.database import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User:
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

# Agrega cualquier otra lógica relacionada con usuarios aquí

def cryptpass(password: str):
    # Genera el hash de la contraseña
    hashed_password = pwd_context.hash(password)
    return hashed_password

## Inicio de Sesión (Log In):

# def get_current_user(request: Request, db:Session):
#     body = {"request":request, 
#             "session":False, 
#             "rol":4, 
#             "msg":None,
#             "USERNAME": None }
#     try:
#         user_id = request.cookies.get("user")
#         print("Find user cookie = ",user_id)
        
#         if user_id is None:
#             print("User cookie not found")
            
#             return None, body
        
#         user = db.query(Users).filter(Users.id == user_id).first()
#         if user is None:
#             print("User not found on db")
#             return None, body
#         print(f"User {user.name} found on db")
#         body["rol"] = user.rol_id
#         body["session"] = True
#         body["USERNAME"] = user.name
#         return user, body
#     except:
#         return None, body