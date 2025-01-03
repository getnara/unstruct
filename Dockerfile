FROM --platform=linux/amd64 python:3.12.6-slim

# Install system dependencies
RUN apt-get update -qq && apt-get install -y -qq \n    gdal-bin binutils libproj-dev libgdal-dev cmake ffmpeg curl &&\n    apt-get clean all &&\n    rm -rf /var/apt/lists/* &&\n    rm -rf /var/cache/apt/*

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Copy the Django project
COPY nara_backend /app/nara_backend/
COPY requirements.txt /app/

# Install dependencies
RUN pip install gunicorn
RUN pip install -r /app/requirements.txt

# Make scripts executable
RUN chmod +x /app/nara_backend/nara_backend/scripts/*.sh

EXPOSE 8000
WORKDIR /app/nara_backend

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/bin/bash", "/app/nara_backend/nara_backend/scripts/run_server.sh"]
