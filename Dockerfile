FROM python:3.9-bullseye
WORKDIR /project
RUN apt-get update -y
RUN apt-get install libgirepository1.0-dev ffmpeg libsm6 libxext6 -y
RUN mkdir /project
RUN cd /project
COPY ./ ./
RUN pip3 install -r /project/requirements.txt
CMD ["make", "celery-debian"]
