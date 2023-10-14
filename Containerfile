FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

ARG DISCORD_TOKEN

COPY wipeingway.py .

CMD [ "python", "wipeingway.py" ]