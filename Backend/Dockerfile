FROM python:3.13-slim

# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/ .

# Cloud Run expects $PORT environment variable
ENV PORT 8080

# Start Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]
