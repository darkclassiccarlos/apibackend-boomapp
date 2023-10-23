# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from passlib.context import CryptContext

#local imports
from ..dependencies import (cryptpass,create_jwt_token,get_current_user)
from ..db.database import get_db
from ..db.db_models import users, roluser
from ..db.models import UserBase,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm,UserBaseUpdate
from ..db import users_actions

pwd_cxt = CryptContext(schemes='bcrypt')

router = APIRouter(
    prefix="/users",
    tags=['users']
)
class Hash():
    def bcrypt(password:str):
        return pwd_cxt.hash(password)
    def verify(hased_password, plain_password):
        return pwd_cxt.verify(plain_password, hased_password)

@router.get("/check")
def root():
   return {'msg': "Hola amigos Boom "}

#Obtener un usuario por ID
@router.get("/{user_id}")
def read_user(user_id: int, db = Depends(get_db)):
    try:
        print(user_id)
        user_db = db.query(users).filter(users.id == user_id).first()
        print(user_db)
        if user_db is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user_db
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error en la base de datos")

#Actualizar un usuario por  ID
@router.post('/update_user/{id}')
async def update_user(request: Request, response:Response, id:int, user_update: UserBaseUpdate, db: Session = Depends(get_db)):
    try:
        edit_user = db.query(users).filter(users.id == id).first()
        if not edit_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        formdata = await request.form()
        edit_user.name = user_update.fullName
        edit_user.password = Hash.bcrypt(user_update.password)
        edit_user.rol_id = user_update.rol_id
        updated_user = users_actions.update_user(db=db, user=edit_user)
        return {f"updated_user"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error en la base de datos")
