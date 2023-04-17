FROM python:3.11-alpine

WORKDIR /freevbucks
RUN pip install --no-cache bs4 lxml requests discord_webhook schedule pytz

COPY main.py .

CMD [ "python", "main.py" ]
