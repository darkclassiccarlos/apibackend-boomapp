from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


plain_password = "contraseña_del_usuario"
print(plain_password)
# Genera el hash de la contraseña
hashed_password = pwd_context.hash(plain_password)

print(hashed_password)