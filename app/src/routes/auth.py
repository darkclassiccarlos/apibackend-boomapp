
from fastapi import APIRouter, Response, Depends, HTTPException, Request, status,Header
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime,timedelta
from typing import Annotated
import jwt

from src.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

#local imports
from ..dependencies import (
    authenticate_user,
    create_access_token, 
    cryptpass,create_jwt_token,
    # get_current_user,
    enviar_correo,
    get_current_active_user,
    decode_jwt_token
    )
from ..db.database import get_db
from ..db.db_models import users, roluser, passwordRecoveryRequest
from ..db.models import Token, UserBase,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm,emailRequest,PasswordRecovery,recoveryPassword
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


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db) 
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(db: Session = Depends(get_db)):
    # logica para poner en lista negra los tokes 
    return "sesión cerrada"

# Ruta para registrar un usuario
@router.post("/register/")
def register_user(userdb: UserBase, db = Depends(get_db)):
    # Verifica si el usuario ya existe
    passwhordhash = cryptpass(userdb.password)
    db_user = users(name=userdb.fullName, password=passwhordhash, email =userdb.email, rol_id = userdb.rol_id)
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
        return JSONResponse(content={"error":"Usuario no registrado"}, status_code=401)

@router.post("/forgot_pass")
def forgot_pass(form_data: emailRequest, db: Session = Depends(get_db)):
    user_email = db.query(users).filter(users.email == form_data.email).first()
    if user_email is None:
        raise HTTPException(status_code=401, detail="El usuario no existe")    
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    data = {"user_id": user_email.id,
            "date": formatted_date_time
            }
    token_recovery_password = create_jwt_token(data)
    db_rquest_recovery = passwordRecoveryRequest(users_id=user_email.id, token=token_recovery_password, date_request =now)
    rquest_recovery = db.query(passwordRecoveryRequest).filter(passwordRecoveryRequest.users_id == user_email.id).first()
    if rquest_recovery:
        delta_request = now - rquest_recovery.date_request
    else:
        delta_request = now
    if rquest_recovery and delta_request <= timedelta(minutes=5):
        raise HTTPException(status_code=401, detail="Ya hay una petición en curso")
    try:
        db.add(db_rquest_recovery)
        db.commit()  # Confirma la transacción
        db.refresh(db_rquest_recovery)
        #return {"request success"}
        #url = "https://boom-backend-test.onrender.com/auth/recover_password/?token="+f"{token_recovery_password}"
        url = "https://wsa-dev.boomtel.com.co/auth/reset-password?token="+f"{token_recovery_password}"
        # Crea el nuevo usuario
        response = enviar_correo(form_data.email, "Recovery Passtword", url)
        return {"response":"sending token"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="No se pudo enviar el token")
    

@router.post("/validate_token")
async def validate_token(token: str = Header(None), db = Depends(get_db)):
    try:
        payload = decode_jwt_token(token)
        if payload:
            expiration_time = datetime.utcfromtimestamp(payload.get("exp", 0))
        else:
            return JSONResponse(content={"success":False, "error":"El token ha expirado"}, status_code=401)
        if datetime.utcnow() > expiration_time:
            return JSONResponse(content={"success":False, "error":"El token ha expirado"}, status_code=401)
        else:
            rquest_recovery = db.query(passwordRecoveryRequest).filter(passwordRecoveryRequest.token == recoveryPassword).first()
            response = {
                "success": True,
                "message": "Usuario validado"
            }
            return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token no válido")

@router.get("/desktop_test")
def desktop_test(user: Annotated[str, Depends(get_current_active_user)]):
    return "prueba de escritorio"
