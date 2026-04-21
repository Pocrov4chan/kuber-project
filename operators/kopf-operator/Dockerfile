FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY handlers.py .
USER 1000
CMD ["kopf", "run", "--standalone", "--all-namespaces", "/app/handlers.py"]
