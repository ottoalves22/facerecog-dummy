FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential

RUN apt-get install -y cmake

RUN apt-get install -y python3-opencv

RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev

RUN apt-get install ffmpeg libsm6 libxext6  freeglut3 freeglut3-dev libxi-dev libxmu-dev -y  

RUN  apt-get update && \
     pip install -r requirements.txt

COPY ./app /app

COPY template.html /app

COPY settings.ini /app

COPY .env /app

RUN mkdir /app/static
