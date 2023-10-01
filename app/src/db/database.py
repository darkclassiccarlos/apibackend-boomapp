from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


HOST = '212.1.211.45'
DATABASE = 'u921098192_db_app_boom'
USERNAME = 'u921098192_dbuser'
PASSWORD = '2021Boom*'

#Mysql arguments
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:3306/{DATABASE}"
engine = create_engine(
     SQLALCHEMY_DATABASE_URL,
     pool_size=20,
     pool_recycle=3600,
     pool_pre_ping=True
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