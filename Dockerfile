FROM python:3.12.6
RUN apt-get update -qq && apt-get install -y -qq \
    gdal-bin binutils libproj-dev libgdal-dev cmake ffmpeg &&\
    apt-get clean all &&\
    rm -rf /var/apt/lists/* &&\
    rm -rf /var/cache/apt/*
ENV PYTHONUNBUFFERED 1
WORKDIR /nara-backend
RUN pip install gunicorn
RUN pip install -r /app/nara_backend/requirements.txt
RUN chmod +x /app/nara_backend/scripts/*.sh
EXPOSE 8000
ENTRYPOINT ["/app/nara_backend/scripts/run_server.sh"]

