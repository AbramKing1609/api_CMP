# Imagen base con Python
FROM python:3.11-slim

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema (Firefox + geckodriver)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    firefox-esr \
    wget \
    curl \
    unzip \
    xvfb \
    ca-certificates \
    gnupg \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copiar el proyecto
WORKDIR /app
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto (Render lo ignora, pero ayuda localmente)
EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
