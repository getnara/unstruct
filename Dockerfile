FROM python:3.12.6
RUN apt-get update -qq && apt-get install -y -qq \
    gdal-bin binutils libproj-dev libgdal-dev cmake ffmpeg &&\
    apt-get clean all &&\
    rm -rf /var/apt/lists/* &&\
    rm -rf /var/cache/apt/*

ENV PYTHONUNBUFFERED 1
WORKDIR /app/nara_backend

# Copy everything to the working directory
COPY . .

# Install dependencies
RUN pip install gunicorn
RUN pip install -r requirements.txt

# Make scripts executable (update path to match actual location)
RUN chmod +x scripts/*.sh

EXPOSE 8000
# Update entrypoint to use correct script path
ENTRYPOINT ["scripts/run_server.sh"]