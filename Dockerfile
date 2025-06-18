# 1) Base
FROM python:3.10-slim

# 2) Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3) Copia y instala deps en build
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 4) Copia todo tu proyecto
COPY . .

# 5) Sitúate en el subdirectorio donde están main.py y database.py
WORKDIR /app/backend

# 6) Exponer puerto y arrancar
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
