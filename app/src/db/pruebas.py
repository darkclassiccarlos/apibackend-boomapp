import mysql.connector
from database import SessionLocal
from db_models import users

db = database.SessionLocal()

users = db.query(db_models.users).all()

print(users)

#############

# HOST = '212.1.211.45'
# DATABASE = 'u921098192_db_app_boom'
# USERNAME = 'u921098192_dbuser'
# PASSWORD = '2021Boom*'

# print(HOST,DATABASE)
# config = {
#     'user': USERNAME,
#     'password': PASSWORD,
#     'host': HOST,
#     'database': DATABASE
# }

# connection = mysql.connector.connect(**config)
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM users where id = 1")
# resultados = cursor.fetchall()
# print(resultados)
# for fila in resultados:
#     print(fila)
#insert
# connection = mysql.connector.connect(**config)
# cursor = connection.cursor()
# query = "INSERT INTO users (user, password) VALUES (%s, %s)"
# values = ("castawq4plastica", "$2b$12$IZ2pK3SCI4Y8AcuHj7l4m.PWmmpFpsgbr1H/.RgNG/AqUZ9rUp28i")
# cursor.execute(query, values)
# # Confirma la transacción
# connection.commit()