FROM python:3.10.10-slim-bullseye
WORKDIR /project
RUN apt-get clean
RUN apt-get update -y
RUN apt-get install git libgirepository1.0-dev libcairo2-dev ffmpeg libsm6 libxext6 libcurl4-openssl-dev libssl-dev -y
# todo: install poetry, then poetry install; remove requirements.txt
COPY requirements.txt requirements.txt
RUN TMPDIR='/var/tmp' pip3 install -r /project/requirements.txt
RUN rm requirements.txt
EXPOSE 8000
# creates a celery worker; can be overwritten by docker-compose to start the API instead
CMD ["make", "celery-debian"]
