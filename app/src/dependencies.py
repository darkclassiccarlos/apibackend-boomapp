# Script para funciones auxiliares
# user_functions.py
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session
import base64
from io import BytesIO
import segno
import os

from typing import Annotated, Dict, Optional
import mysql.connector
#from .models import User,UserLogin
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .db.database import get_db
import jwt
from datetime import datetime, timedelta
from .db.db_models import users, roluser, familys, products,familyproducts

from .db.models import (
    TokenData,
)

from src.settings import (
    SECRET_KEY,
    ALGORITHM,
)


# smtp librarys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


db = next(get_db())




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Clave secreta para firmar el token (deberías guardarse esto de manera segura per ya vemos)
SECRET_KEY = "tu_clave_secreta"
# Tiempo de expiración del token (en segundos)
TOKEN_EXPIRATION = timedelta(minutes=15)

class User:
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

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

def decode_jwt_token(data):
    try:
        return jwt.decode(data, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        print(e)
        return None

def get_current_user(request: Request, db:Session):
    body = {"request":request, 
            "session":False, 
            "rol":4, 
            "msg":None,
            "USERNAME": None }
    print(body)
    try:
        user_id = request.cookies.get("user")
        print("Find user cookie = ",user_id)
        
        if user_id is None:
            print("User cookie not found")
            
            return None, body
        
        user = db.query(users).filter(users.id == user_id).first()
        if user is None:
            print("User not found on db")
            return None, body
        print(f"User {user.name} found on db")
        body["rol"] = user.rol_id
        body["session"] = True
        body["USERNAME"] = user.name
        return user, body
    except:
        return None, body


# ----------------------------------------------------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    user = db.query(
        users.email,
        users.name,
        users.picture,
        users.password,
        users.id,
        users.is_active       
        ).filter(users.email == username).first()
    return user


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    
    user = user._asdict()
    user["picture"] = f"assets/images/{user['picture']}.png"
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    global db
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    try: 
        user = get_user(db, username=token_data.username)
    except mysql.connector.Error as err:
        db = next(get_db())
        user = get_user(db, username=token_data.username)
    
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):  
    if current_user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return True


# ======================================================================================================================
def enviar_correo(destinatario, asunto, mensaje):
    # Configura tus credenciales de Gmail
    remitente = 'contacto@boomtel.com.co'  # Tu dirección de smtp
    contraseña = 'Contacto123*'     # Tu contraseña de smtp

    servidor_smtp = smtplib.SMTP('smtp.hostinger.com', 587)
    servidor_smtp.starttls()
    servidor_smtp.login(remitente, contraseña)

    mensaje_correo = MIMEMultipart()
    mensaje_correo['From'] = remitente
    mensaje_correo['To'] = destinatario
    mensaje_correo['Subject'] = asunto

    mensaje_correo.attach(MIMEText(mensaje, 'plain'))
    servidor_smtp.sendmail(remitente, destinatario, mensaje_correo.as_string())

    servidor_smtp.quit()


def update_entity(entityupdate, db: Session):
    db.add(entityupdate)
    db.commit()
    db.refresh(entityupdate)
    return entityupdate


def remove_products_familys(db: Session, familia_id: int):
    familyProductIds = db.query(familyproducts).filter(familyproducts.family_id==familia_id).all()
    if familyProductIds:
        productsToDelete = len(familyProductIds)
        for familyProductId in familyProductIds:
            db.delete(familyProductId)
            db.commit()
            #db.refresh(familyproducts)
            print(familyProductId.product_id)
            producto = db.query(products).filter(products.id == familyProductId.product_id).first()
            db.delete(producto)
            db.commit()
            #db.refresh(products)
        return {"elementos eliminados":productsToDelete}
    else:
        return {"No existe elementos para borrar"}


def remove_products(db: Session, product_id: int):
    familyProductIds = db.query(familyproducts).filter(familyproducts.product_id==product_id).first()
    if familyProductIds:
        db.delete(familyProductIds)
        db.commit()
        #db.refresh(familyproducts)
        producto = db.query(products).filter(products.id == product_id).first()
        db.delete(producto)
        db.commit()
        #db.refresh(products)
        return {"elemento eliminado":producto.name}
    else:
        return {"No existe elementos para borrar"}

def create_business_qr(data):
    data = f"{data}.boomtel.com.co"
    buffered = BytesIO()
    qr = segno.make_qr(data)
    qr.save(buffered, kind= "png", scale=9, border=1)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def create_website(data):
    response = data.replace(" ", "").lower()
    return response
