# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from .dependencies import (cryptpass,create_jwt_token,get_current_user)

from .db.database import get_db
from .db.db_models import users, roluser
from .db.models import UserBase,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm
from . db import users_actions
from sqlalchemy.orm import Session

#from .settings import ()

router = APIRouter()

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


@router.get("/check")
def root():
   return {'msg': "Hola amigos Boom "}

#Obtener un usuario por ID
@router.get("/users/{user_id}")
def read_user(user_id: int, db = Depends(get_db)):
    try:
        user_db = db.query(users).filter(users.id == user_id).first()
        if user_db is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user_db
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error en la base de datos")

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

# Ruta de inicio de sesión (Log In):
@router.post("/login")
async def login(request: Request,
                response: Response,
                form_data: CustomOAuth2PasswordRequestForm, # = Depends(),
                #form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    #try:
    form = LoginForm(request)
    await form.create_oauth_form()
    #response = RedirectResponse(url='/home', status_code=status.HTTP_302_FOUND)
    user = users_actions.authenticate_user(db=db,
                                        email=form_data.email,
                                        password=form_data.password)
    if user:
        #response.set_cookie(key="user",value=user.id, httponly=True)
        #USERNAME = user.user
        #return response
        user=user.as_dict()
        user = {
            "name": user["name"],  # Puedes utilizar otro campo si tienes el nombre en la base de datos
            "picture": f"assets/images/{user['picture']}.png",
            "email": user["email"]
        }
        token = create_jwt_token(user)
        return {"access_token": token, "token_type": "bearer"}

    else: 
        #raise HTTPException(status_code=404, detail="Incorrect Username or Password")
        #return templates.TemplateResponse('login.html', {"request":request, "session":False, "msg":"Incorrect Username or Password", "rol":4})
        return "Incorrect Username or Password"
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=500, detail="Unkwon error")
