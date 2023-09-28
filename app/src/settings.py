# from dataclasses import dataclass
# import os
# from dotenv import load_dotenv
# from pathlib import Path
# import pyodbc

# from sqlalchemy import create_engine, MetaData
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
# import urllib
# from sqlalchemy.sql import text

# from config.transactionDB.start_db import int_sqlite

# int_sqlite()

# try: PROD_MODE = eval(os.environ.get("PROD_MODE"))
# except: PROD_MODE = False

# if PROD_MODE:
#     print("PROD_MODE: production")
#     dotenv_path = Path('./config/prod.env')
# else:
#     print("PROD_MODE: development")
#     dotenv_path = Path('./config/dev.env')


# load_dotenv(dotenv_path=dotenv_path)


# @dataclass
# class EnvVars:
#     #DRIVER = "ODBC Driver 17 for SQL Server"

#     HOSTTINGER_HOST: str = os.getenv("HOSTTINGER_HOST")
#     HOSTTINGER_DB: str = os.getenv("HOSTTINGER_DB")
#     HOSTTINGER_USER: str = os.getenv("HOSTTINGER_USER")
#     HOSTTINGER_PWD: str = os.getenv("HOSTTINGER_PWD")

# class DbObj(EnvVars):
#     def __init__(self):
#         params = urllib.parse.quote_plus('Driver={};Server={};Database={};UID={};PWD={}'.format(
#                                                                                         self.DRIVER, 
#                                                                                         self.HOSTTINGER_HOST, 
#                                                                                         self.HOSTTINGER_DB, 
#                                                                                         self.HOSTTINGER_USER, 
#                                                                                         self.HOSTTINGER_PWD 
#                                                                                        ))
        
#         self.engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params), poolclass=NullPool)
#         self.meta = MetaData()

#     @property
#     def get_engine(self):
#         return self.engine
    
#     @property
#     def get_meta(self):
#         return self.meta

#     def db_engine(self):
#         engine = self.get_engine
#         session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
#         try:
#             db = session()
#             yield db
        
#         finally:
#             db.close()

# db_manager = DbObj()