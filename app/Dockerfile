FROM python:3.11.5-slim

WORKDIR /app
RUN apt-get update

# Paquete conexion mssql a Python
#RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
#RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
#RUN apt-get update

# Soporte binarios Multiarch
#RUN curl http://ftp.br.debian.org/debian/pool/main/g/glibc/multiarch-support_2.28-10+deb10u1_amd64.deb > multiarch-support_2.28-10+deb10u1_amd64.deb
#RUN dpkg -i multiarch-support_2.28-10+deb10u1_amd64.deb

# Paquete de C++ para conexion a mssql
# RUN apt-get install g++
# RUN ACCEPT_EULA=Y apt-get install msodbcsql17 -y
# RUN apt-get install unixodbc-dev -y
# RUN apt-get install rsync -y

COPY requirements.txt requirements.txt
# Instalacion de paquetes
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY main.py main.py
COPY src src
COPY config config

# # Tener en cuenta proyectos siguientes
# RUN chmod +rwx /etc/ssl/openssl.cnf
# RUN sed -i 's/TLSv1.2/TLSv1/g' /etc/ssl/openssl.cnf
# RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/g' /etc/ssl/openssl.cnf

EXPOSE 80

# COPY ./app .
# RUN chmod -R -f 777 /app
# USER 1000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]
