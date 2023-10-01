from sqlalchemy.orm.session import Session
from passlib.context import CryptContext

from .database import SessionLocal
from .db_models import users, roluser
from .models import UserBase, UserBaseUpdate

pwd_cxt = CryptContext(schemes='bcrypt')

class Hash():
    def bcrypt(password:str):
        return pwd_cxt.hash(password)
    def verify(hased_password, plain_password):
        return pwd_cxt.verify(plain_password, hased_password)

def authenticate_user(db:Session, email: str, password: str) -> users | bool:
    user_db = db.query(users).filter(users.email == email).first()
    if not user_db:
        return False
    if not Hash.verify(hased_password= user_db.password, plain_password=password):
        return False
    return user_db

def create_user(db: Session, user: UserBase) -> users | str:
    users = db.query(users.name, users.email).all()
    _roles = db.query(roluser.id).all()
    
    if any(user.name in tpl for tpl in users):
        print("name already in use")
        return "name already in use"
    elif any(user.email in tpl for tpl in users):
        print("email already in use")
        return "email already in use"
    elif any(user.rol_id in tpl for tpl in _roles) == False:
        print("invalid rol")
        return "invalid rol"

    else:
        try:
            new_user = users()
            new_user.name = users.name.lower()
            new_user.email = users.email.lower()
            new_user.password = Hash.bcrypt(users.password)
            new_user.rol_id = users.rol_id if users.rol_id is not None else 2

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except Exception as e:
            return str(e)

        return new_user

def update_user(db: Session, user : UserBaseUpdate) -> users | None:
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user