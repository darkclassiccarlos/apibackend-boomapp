from sqlalchemy.orm.session import Session
from passlib.context import CryptContext

from .database import SessionLocal
from .db_models import users, rol_user
from .models import UserBase


pwd_cxt = CryptContext(schemes='bcrypt')


class Hash():
    def bcrypt(password:str):
        return pwd_cxt.hash(password)
    def verify(hased_password, plain_password):
        return pwd_cxt.verify(plain_password, hased_password)

def authenticate_user(db:Session, user: str, password: str) -> users | bool:
    user_db = db.query(users).filter(users.user == user).first()
    if not user_db:
        return False
    if not Hash.verify(hased_password= user_db.password, plain_password=password):
        return False
    return user_db