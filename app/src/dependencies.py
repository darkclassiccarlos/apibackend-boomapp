# Script para funciones auxiliares
# user_functions.py

from typing import Dict, Optional
import mysql.connector
#from .models import User,UserLogin
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .db.database import get_db
import jwt
from datetime import datetime, timedelta


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Clave secreta para firmar el token (deberías guardarse esto de manera segura per ya vemos)
SECRET_KEY = "tu_clave_secreta"
# Tiempo de expiración del token (en segundos)
TOKEN_EXPIRATION = timedelta(minutes=30)

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

# Función para crear un token JWT
def create_jwt_token(data):
    expiration = datetime.utcnow() + TOKEN_EXPIRATION
    print(expiration)
    payload = {
        "exp": expiration,
        **data
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")