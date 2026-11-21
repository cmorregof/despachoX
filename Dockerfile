# DespachoX en un solo contenedor: bot de Telegram + tablero + optimizador, con una base SQLite en /data.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt despliegue/restricciones.txt ./
RUN pip install -r requirements.txt -c restricciones.txt
COPY . .
CMD ["bash", "despliegue/arranque.sh"]
