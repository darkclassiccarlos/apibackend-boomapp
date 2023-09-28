# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from .orm.tables import (users_table)
#from sqlalchemy.orm import session
from .models import User,UserLogin
from passlib.hash import bcrypt  # Importa la biblioteca de hashing

from .dependencies import (get_user, get_user_by_username,create_user,oauth2_form_to_user_login,cryptpass)

#from .settings import ()

router = APIRouter()

@router.get("/check")
def root():
   return {'msg': "Hola amigos Boom "}

# Obtener un usuario por ID
@router.get("/users/{user_id}")
def read_user(user_id: int):
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Ruta para registrar un usuario
@router.post("/register/")
def register_user(username: str, password: str):
    # Verifica si el usuario ya existe
    user = get_user_by_username(username)
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    # Crea el nuevo usuario
    user = User(user=username, password=password)
    print(user)
    #crud.create_user(db, user)
    create_user(user)
    return {"message": "Usuario registrado correctamente"}


# Ruta de inicio de sesión (Log In):
@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()):
    user = oauth2_form_to_user_login(user)
    username = user.username
    password = cryptpass(user.password)
    print(user)
    print(password)
    #try:
    user_db = get_user_by_username(username)
    print(user_db)
    bcrypt_context = bcrypt.using(salt_size=12).from_string(user_db[2])

    if user_db and len(user_db) >= 3 and bcrypt.verify(password, user_db[2]):
    if user_db and len(user_db) >= 3 and bcrypt.verify(password, user_db[2]):
        return {"message": "Inicio de sesión exitoso", "username": user.username}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    #except Exception as e:
    #    raise HTTPException(status_code=500, detail="Error en la base de datos")
