#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6
FROM nvidia/cuda:10.1-cudnn7-devel

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
        libpng-dev libjpeg-dev python3-opencv ca-certificates \
        python3-dev build-essential pkg-config git curl wget automake libtool && \
  rm -rf /var/lib/apt/lists/*

RUN curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
        python3 get-pip.py && \
        rm get-pip.py

#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6
RUN pip install --no-cache-dir uvicorn gunicorn fastapi aiofiles torch==1.3.1 torchvision==0.4.2 opencv-python pafy youtube_dl pillow==8.1.1 scipy Jinja2 python-multipart numpy==1.14.5

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

#Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]

