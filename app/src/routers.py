# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from .dependencies import (cryptpass,create_jwt_token)

from .db.database import get_db
from .db.db_models import users
from .db.models import UserBase,RolBase,FamilyproductsBase,FamilysBase,ProductsBase
from . db import users_actions
from sqlalchemy.orm import Session

#from .settings import ()

router = APIRouter()

# Loginform class for the login page
class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('username')
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
    db_user = users(user=userdb.user, picture=userdb.picture ,password=passwhordhash, email =userdb.email, rol_id = userdb.rol_id)
    print(db_user)
    user_db = db.query(users).filter(users.user == userdb.user).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    # Crea el nuevo usuario
    db.add(db_user)
    db.commit()  # Confirma la transacción
    db.refresh(db_user)  
    return {"message": "Usuario registrado correctamente"}

# @router.post('/update_user/{id}')
# async def update_user(request: Request, response:Response, id:int, db: Session = Depends(get_db)):
#     print("Editing user page")
#     user, body = get_current_user(request=request, db=db)
#     if user is None:
#         raise HTTPException(status_code=404, detail="Usuario no valido")
#     if user.rol_id != 1:
#         body["msg"] = "Unauthorized user getting back to home page"
#         return templates.TemplateResponse("home.html", body)
#     edit_user = db.query(Users).filter(Users.id == id).first()
#     formdata = await request.form()
#     edit_user.name = formdata['name'].lower()
#     edit_user.last_name = formdata['last_name'].lower()
#     edit_user.email = formdata['email'].lower()
#     edit_user.password = edit_user.password if formdata['password'] =="" or formdata['password'] is None else  users_actions.Hash.bcrypt(formdata['password'])
#     edit_user.rol_id = formdata['rol']
#     updated_user = users_actions.update_user(db=db, user=user)
    
#     return RedirectResponse(url="/users/users", status_code=status.HTTP_302_FOUND)

# Ruta de inicio de sesión (Log In):
@router.post("/login")
async def login(request: Request,
                response: Response,
                form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        #response = RedirectResponse(url='/home', status_code=status.HTTP_302_FOUND)
        user = users_actions.authenticate_user(db=db,
                                            user=form_data.username,
                                            password=form_data.password)
        if user:
            #response.set_cookie(key="user",value=user.id, httponly=True)
            #USERNAME = user.user
            #return response
            user=user.as_dict()
            user = {
                "name": user["user"],  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                "picture": f"assets/images/{user['picture']}.png",
                "email": user["email"]
            }
            token = create_jwt_token(user)
            return {"access_token": token, "token_type": "bearer"}

        else: 
            #raise HTTPException(status_code=404, detail="Incorrect Username or Password")
            #return templates.TemplateResponse('login.html', {"request":request, "session":False, "msg":"Incorrect Username or Password", "rol":4})
            return "Incorrect Username or Password"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unkwon error")
