# Imagen base de Python
FROM python:3.11-slim

# No pedir confirmaciones
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema (para Chrome + Selenium)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver \
    chromium \
    wget \
    curl \
    unzip \
    xvfb \
    ca-certificates \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
WORKDIR /app
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8000

# Iniciar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
