FROM --platform=linux/amd64 python:3.12.6-slim

# Install system dependencies
RUN apt-get update -qq && apt-get install -y -qq \
    gdal-bin binutils libproj-dev libgdal-dev cmake ffmpeg curl \
    build-essential g++ gcc libc6-dev make pkg-config \
    python3-dev libstdc++6 && \
    apt-get clean all && \
    rm -rf /var/apt/lists/* && \
    rm -rf /var/cache/apt/*

ENV PYTHONUNBUFFERED=1
ENV CFLAGS="-fPIC"
ENV CXXFLAGS="-fPIC -std=c++11"
ENV CC="gcc"
ENV CXX="g++"
ENV PIP_NO_CACHE_DIR=0
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY unstruct_backend/requirements.txt /app/requirements.txt

# Install dependencies with optimizations
RUN pip install --no-cache-dir gunicorn setuptools && \
    pip install --no-cache-dir --use-pep517 -r /app/requirements.txt

# Copy the rest of the application
COPY unstruct_backend /app/unstruct_backend/

# Make scripts executable
RUN chmod +x /app/unstruct_backend/scripts/*.sh

EXPOSE 8000
WORKDIR /app/unstruct_backend

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD curl -f http://localhost:8000/health/ || exit 1 

ENTRYPOINT ["/bin/bash", "/app/unstruct_backend/scripts/run_server.sh"]
