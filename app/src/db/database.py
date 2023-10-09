from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool
import os

# # Especifica la ubicación del archivo .env
dotenv_path = os.path.join(os.path.dirname(__file__), "../../config/prod.env")
load_dotenv(dotenv_path)

HOST = os.getenv("HOSTTINGER_HOST")
USERNAME = os.getenv("HOSTTINGER_USER")
PASSWORD = os.getenv("HOSTTINGER_PWD")
DATABASE = os.getenv("HOSTTINGER_DB")

#Mysql arguments
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:3306/{DATABASE}"
engine = create_engine(
     SQLALCHEMY_DATABASE_URL,
     poolclass=NullPool,
     #pool_size=20,
     pool_recycle=3600,
     #pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

## crear y cierre de sesion 
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()