FROM python:3.8-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc
    

WORKDIR /trust-service
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 3000
USER nobody
CMD ["gunicorn", "-k", "eventlet", "-b", "0.0.0.0:3000", "app:app"]
