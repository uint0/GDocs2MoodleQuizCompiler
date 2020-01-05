FROM python:3.8.0-alpine
WORKDIR /app

RUN apk upgrade && apk add git libreoffice
COPY . /app
RUN pip install -r requirements.txt
RUN mkdir -p uploads

CMD gunicorn -b 0.0.0.0:8000 app:app

