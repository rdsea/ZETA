FROM python:3.8-slim

WORKDIR /policy-evaluation
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

USER nobody
CMD ["gunicorn",  "-b", "0.0.0.0:3001", "app:app"]
