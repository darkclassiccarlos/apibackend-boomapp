# from sqlalchemy import create_engine

# # Configura los parámetros de conexión
# user = 'u921098192_dbuser'
# password = '2021Boom*'
# host = '212.1.211.45'  # O la dirección de tu servidor MySQL
# database = 'u921098192_db_app_boom'

# # HOST = '212.1.211.45'
# # DATABASE = 'u921098192_db_app_boom'
# # USERNAME = 'u921098192_dbuser'
# # PASSWORD = '2021Boom*'

# # Crea la cadena de conexión SQLAlchemy
# connection_string = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'

# # Crea una instancia de la conexión SQLAlchemy
# engine = create_engine(connection_string)

# # Ejemplo de consulta SQL
# query = "SELECT * FROM users"

# # Ejecuta la consulta y obtén los resultados
# with engine.connect() as connection:
#     result = connection.execute(query)
#     for row in result:
#         print(row)