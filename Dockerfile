FROM python:3.12-alpine

WORKDIR /freevbucks
COPY . .

RUN pip install --no-cache -r requirements.txt

CMD [ "python", "main.py" ]
