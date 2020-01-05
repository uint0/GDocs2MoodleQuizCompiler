FROM python:3.8.0-slim-buster
WORKDIR /app

RUN apt-get update && apt-get install -y git libreoffice-writer
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src ./src
COPY app.py .
RUN mkdir -p uploads

CMD gunicorn -b 0.0.0.0:8000 app:app

