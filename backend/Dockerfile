# Dockerfile

# Use a lightweight official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first (for build cache efficiency)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Cloud Run expects the application to listen on the port specified by the PORT environment variable (default 8080)
# We do NOT use EXPOSE here, as Cloud Run manages the port.

# Use Gunicorn to run the application securely and efficiently
# The command format is: gunicorn --bind [HOST]:[PORT] [MODULE_NAME]:[FLASK_APP_VARIABLE]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
