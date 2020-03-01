# Dockerfile

FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev jpeg-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN apk --update add bash nano git
COPY . /app

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

