# Script para funciones auxiliares
# user_functions.py

from typing import Dict, Optional
import mysql.connector
from .models import User,UserLogin
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


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

def read_user(user_id: int):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def red_user_by_username(username: str):
    query = f"SELECT * FROM users WHERE user = '{username}'"
    return query

def insert_user():
    query = "INSERT INTO users (user, password) VALUES (%s, %s)"
    return query


def configdb():
    HOST = '212.1.211.45'
    DATABASE = 'u921098192_db_app_boom'
    USERNAME = 'u921098192_dbuser'
    PASSWORD = '2021Boom*'
    config = {
        'user': USERNAME,
        'password': PASSWORD,
        'host': HOST,
        'database': DATABASE
    }
    return config

def get_user(user_id: int) -> Optional[User]:
    config = configdb()
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = read_user(user_id)
    cursor.execute(query)
    resultados = cursor.fetchall()
    return resultados

def get_user_by_username(username: str):
    config = configdb()
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = red_user_by_username(username)
    cursor.execute(query)
    resultados = cursor.fetchall()
    if resultados:
        print('usuario ya exite')
    return resultados

## Registrar usuario
def create_user(user: User):
    config = configdb()
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cryptpassword = cryptpass(user.password)
    query = insert_user()
    values = (user.user, cryptpassword)
    cursor.execute(query,values)
    connection.commit()
## Inicio de Sesión (Log In):

def oauth2_form_to_user_login(form: OAuth2PasswordRequestForm) -> UserLogin:
    return UserLogin(username=form.username, password=form.password)