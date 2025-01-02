FROM python:3.12.6
RUN apt-get update -qq && apt-get install -y -qq \
    gdal-bin binutils libproj-dev libgdal-dev cmake ffmpeg &&\
    apt-get clean all &&\
    rm -rf /var/apt/lists/* &&\
    rm -rf /var/cache/apt/*

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Copy the Django project
COPY . /app/

# Install dependencies
RUN pip install gunicorn
RUN pip install -r requirements.txt

# Make scripts executable
RUN chmod +x /app/nara_backend/scripts/*.sh

EXPOSE 8000
WORKDIR /app/nara_backend
ENTRYPOINT ["/app/nara_backend/scripts/run_server.sh"]