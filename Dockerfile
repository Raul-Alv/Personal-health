# Dockerfile
FROM python:3.10-slim

# No escribir archivos .pyc, evitar buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definimos /app como directorio de trabajo
WORKDIR /app

# Copiamos solo el entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# El entrypoint se encargará de pip install al arrancar
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto: arranca Uvicorn apuntando a main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]