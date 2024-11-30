FROM python:3.12.6
RUN apt-get update -qq && apt-get install -y -qq \
    gdal-bin binutils libproj-dev libgdal-dev cmake ffmpeg &&\
    apt-get clean all &&\
    rm -rf /var/apt/lists/* &&\
    rm -rf /var/cache/apt/*
ENV PYTHONUNBUFFERED 1
WORKDIR /app/nara_backend
COPY requirements.txt .
RUN pip install gunicorn && \
    pip install -r requirements.txt
COPY . .
RUN chmod +x nara_backend/scripts/*.sh
EXPOSE 8000
ENTRYPOINT ["nara_backend/scripts/run_server.sh"]

