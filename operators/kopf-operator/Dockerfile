FROM python:3.12-slim
RUN useradd --uid 1000 --create-home --shell /bin/sh kopf
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY handlers.py .
USER kopf
CMD ["kopf", "run", "--standalone", "--all-namespaces", "/app/handlers.py"]
