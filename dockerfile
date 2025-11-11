# Usa una imagen base de Python versión 3.9
# Esta imagen ya trae instalado Python y sus herramientas básicas.
FROM python:3.9

# Actualiza los paquetes del sistema e instala el cliente SSH
# Esto permite realizar conexiones seguras o descargar código desde repositorios privados.
RUN apt-get update && apt-get install -y openssh-client

# Define una variable de entorno que evita que Python guarde el buffer de salida,
# lo que hace que los mensajes (logs) se muestren en tiempo real en la consola de Docker.
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo dentro del contenedor.
# A partir de aquí, todos los comandos se ejecutarán dentro de /app.
WORKDIR /app

# Copia el archivo requirements.txt desde tu proyecto local
# al directorio /app dentro del contenedor.
COPY requirements.txt /app/requirements.txt

# Instala las dependencias de Python especificadas en requirements.txt.
# Es el paso donde se instalan los paquetes necesarios (Django, Flask, etc.).
RUN pip install -r requirements.txt

# Copia el resto de la aplicación al contenedor dentro del directorio /app.
# Esto incluye tu código fuente, manage.py, configuraciones, etc.
COPY . /app

# Este comando define la instrucción principal que se ejecutará al iniciar el contenedor.
# 'python manage.py runserver' inicia el servidor de desarrollo de Django.
# '0.0.0.0:8000' indica que el servidor escuche en todas las interfaces de red
# dentro del contenedor, en el puerto 8000, lo que permite acceder a la app desde fuera.
CMD python manage.py runserver 0.0.0.0:8000
