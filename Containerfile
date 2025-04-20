FROM python:3.10-slim-buster

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG DISCORD_TOKEN

CMD [ "python", "bot.py" ]