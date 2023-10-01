# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

#local imports
from ..dependencies import (cryptpass,create_jwt_token,get_current_user)
from ..db.database import get_db
from ..db.db_models import users, roluser
from ..db.models import UserBase,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm
from ..db import users_actions


router = APIRouter(
    prefix="/auth",
    tags=['auth']
)
# Loginform class for the login page
class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.email = form.get('email')
        self.password = form.get('password')

# Ruta de inicio de sesión (Log In):
@router.post("/login")
async def login(request: Request,
                response: Response,
                form_data: CustomOAuth2PasswordRequestForm,
                db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        user = users_actions.authenticate_user(db=db,
                                            email=form_data.email,
                                            password=form_data.password)
        if user:
            user=user.as_dict()
            user = {
                "name": user["name"],  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                "picture": f"assets/images/{user['picture']}.png",
                "email": user["email"]
            }
            token = create_jwt_token(user)
            return {"access_token": token, "token_type": "bearer"}

        else: 
            return "Incorrect Username or Password"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unkwon error")

@router.post("/logout")
def logout(db: Session = Depends(get_db)):
    # logica para poner en lista negra los tokes 
    return "sesión cerrada"

# Ruta para registrar un usuario
@router.post("/register/")
def register_user(userdb: UserBase, db = Depends(get_db)):
    print("Trying user creation")
    # Verifica si el usuario ya existe
    print(userdb)
    passwhordhash = cryptpass(userdb.password)
    db_user = users(name=userdb.fullName, password=passwhordhash, email =userdb.email, rol_id = userdb.rol_id)
    print(db_user)
    user_db = db.query(users).filter(users.name == userdb.fullName).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    # Crea el nuevo usuario
    db.add(db_user)
    db.commit()  # Confirma la transacción
    db.refresh(db_user)  
    return {"message": "Usuario registrado correctamente"}
