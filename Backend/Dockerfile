FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential gcc gfortran libblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install them
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Ensure lxml_html_clean is installed
RUN pip install --no-cache-dir lxml[html_clean]

# Copy your backend code and data
COPY Backend/ .

# Set Cloud Run port
ENV PORT 8080

# Start the app using PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
