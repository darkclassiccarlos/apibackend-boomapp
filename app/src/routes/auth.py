# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request, status,Header
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime,timedelta
import jwt

#local imports
from ..dependencies import (cryptpass,create_jwt_token,get_current_user,enviar_correo,decode_jwt_token)
from ..db.database import get_db
from ..db.db_models import users, roluser, passwordRecoveryRequest
from ..db.models import UserBase,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm,emailRequest,PasswordRecovery,recoveryPassword
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
                "email": user["email"],
                "user_id": user["id"]
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
    user_db = db.query(users).filter(users.email == userdb.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    # Crea el nuevo usuario
    try:
        db.add(db_user)
        db.commit()  # Confirma la transacción
        db.refresh(db_user)
        response = db_user.as_dict()
        response = {
                "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                "message": f"User Registrado {userdb.fullName}",
                "result": userdb.fullName
            }
        token = create_jwt_token(response)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unkwon error")

@router.post("/forgot_pass")
def forgot_pass(form_data: emailRequest, db: Session = Depends(get_db)):
    user_email = db.query(users).filter(users.email == form_data.destinatario).first()
    if user_email is None:
        raise HTTPException(status_code=400, detail="El usuario ya existe")    
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    data = {"user_id": user_email.id,
            "date": formatted_date_time
            }
    token_recovery_password = create_jwt_token(data)
    db_rquest_recovery = passwordRecoveryRequest(users_id=user_email.id, token=token_recovery_password, date_request =now)
    rquest_recovery = db.query(passwordRecoveryRequest).filter(passwordRecoveryRequest.users_id == user_email.id).first()
    print(rquest_recovery)
    if rquest_recovery:
        delta_request = now - rquest_recovery.date_request
        print(delta_request)
    else:
        delta_request = now
        print(delta_request)
    if rquest_recovery and delta_request <= timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="Ya hay una petición en curso")
    try:
        db.add(db_rquest_recovery)
        db.commit()  # Confirma la transacción
        db.refresh(db_rquest_recovery)
        #return {"request success"}
        #url = "https://boom-backend-test.onrender.com/auth/recover_password/?token="+f"{token_recovery_password}"
        url = "https://wsa-dev.boomtel.com.co/auth/reset-password?token="+f"{token_recovery_password}"
        # Crea el nuevo usuario
        response = enviar_correo(form_data.destinatario, "Recovery Passtword", url)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unkwon error")
    

@router.post("/validate_recovery_password")
async def validate_recovery_password(token: str = Header(None), db = Depends(get_db)):
    try:
        payload = decode_jwt_token(token)
        #payload = jwt.decode(token.access_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        if payload:
            expiration_time = datetime.now()
        else:
            expiration_time = datetime.utcfromtimestamp(payload.get("exp", 0))

        if datetime.utcnow() > expiration_time:
            raise HTTPException(status_code=400, detail="El token ha expirado")
        else:
            rquest_recovery = db.query(passwordRecoveryRequest).filter(passwordRecoveryRequest.token == recoveryPassword).first()
            response = {
                "success": True,
                "message": "Usuario validado"
            }
            return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El token ha expirado")
    except jwt.DecodeError:
        raise HTTPException(status_code=400, detail="Token inválido")
