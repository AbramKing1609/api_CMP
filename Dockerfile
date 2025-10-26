# Imagen base liviana
FROM python:3.11-slim

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
