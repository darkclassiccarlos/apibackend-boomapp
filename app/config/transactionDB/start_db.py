import os
import sqlite3

print(os.getcwd())
print(os.listdir())

try:
    os.mkdir("./sqlite")
except:
    pass

conexion = sqlite3.connect("./sqlite/transaction.db")

ddl_files = os.listdir("./config/transactionDB/DDLs")
part_path = "./config/transactionDB/DDLs/"

def int_sqlite():
    for file in ddl_files:
        if file.endswith(".sql"):
            print(file)
            with open(part_path + file, 'r') as sql_file:
                try:
                    conexion.executescript(sql_file.read())
                except sqlite3.OperationalError:
                    print(f"Tabla {file} ya existe")