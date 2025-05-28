# Use a lightweight base image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Command to run Gunicorn for the Flask app and the Extractor
CMD ["sh", "-c", "gunicorn app:app -b 0.0.0.0:8080 & python3 -m Extractor"]
