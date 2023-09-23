import os
from dotenv import load_dotenv
from pathlib import Path

#from MySQLdb import _mysql

import mysql.connector


dotenv_path = Path('./config/dev.env')
load_dotenv(dotenv_path=dotenv_path)


# HOST = os.getenv("HOSTTINGER_HOST")
# DATABASE = os.getenv("HOSTTINGER_DB")
# USERNAME = os.getenv("HOSTTINGER_USER")
# PASSWORD = os.getenv("HOSTTINGER_PWD")
# #SSL_CERT = os.getenv("SSL_CERT")

HOST = '212.1.211.45'
DATABASE = 'u921098192_db_app_boom'
USERNAME = 'u921098192_dbuser'
PASSWORD = '2021Boom*'

print(HOST,DATABASE)
config = {
    'user': USERNAME,
    'password': PASSWORD,
    'host': HOST,
    'database': DATABASE
}

# def get_connection():
#   return _mysql.connect(
#           host= HOST,
#           user= USERNAME,
#           password= PASSWORD,
#           database= DATABASE,
#         #   ssl      = {
#         #     "ca": SSL_CERT
#         #   }
#         )
#connection = get_connection()

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

cursor.execute("SELECT * FROM users")
resultados = cursor.fetchall()
print(resultados)
# for fila in resultados:
#     print(fila)
