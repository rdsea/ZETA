FROM python:3.8-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc
    

WORKDIR /web-server
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 4000
CMD ["gunicorn", "-b", "0.0.0.0:4000", "web_server:app"]
