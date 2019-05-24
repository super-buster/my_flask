FROM python:3.6-alpine

RUN adduser -D flasky

WORKDIR /home/flasky

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN apk --no-cache add build-base
RUN apk --no-cache add postgresql-dev
RUN python3 -m pip install psycopg2

COPY app app
COPY migrations migrations
COPY flasky.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP flasky.py

RUN chown -R flasky:flasky ./
USER flasky

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]