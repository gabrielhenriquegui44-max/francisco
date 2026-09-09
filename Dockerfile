FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Azure App Service for Containers injeta a variável WEBSITES_PORT / PORT;
# Container Apps e Container Instances usam o valor de EXPOSE ou o que for configurado.
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 app:app"]
