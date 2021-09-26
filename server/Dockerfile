# syntax=docker/dockerfile:1

FROM python:3.7-slim-bullseye
WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN apt-get update
RUN apt-get install -y libgl1 libglib2.0-0

COPY . server

CMD [ "python3", "server/manage.py" , "runserver", "--host", "0.0.0.0"]
