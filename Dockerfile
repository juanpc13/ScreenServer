FROM python:3.11-slim

# Crear carpeta de trabajo
WORKDIR /app

# Copiar el archivo Python al contenedor
COPY app.py /app

# Instalar dependencias
RUN pip install flask flask-socketio opencv-python gevent

# Exponer el puerto
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "app.py"]