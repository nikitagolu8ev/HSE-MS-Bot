FROM python:3.11.1

WORKDIR /home

ENV TELEGRAM_API_TOKEN="5942739918:AAGuMNW9fQj7tQO73GyKBKhRXzL4bVUdMyM"
ENV LASTFM_API_KEY="d6fb135d93f7ee7af8ee630444a53731"

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get upgrade -y
RUN pip install -U pip pipenv && apt-get install sqlite3

COPY *.py ./
COPY createdb.sql ./
COPY Pipfile ./
COPY Pipfile.lock ./

RUN pip install -U pip pipenv && apt update && apt install sqlite3
RUN pipenv install --deploy --ignore-pipfile

CMD ["pipenv", "run", "python", "main.py"]
