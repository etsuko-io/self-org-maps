install:
	pip install -r requirements.txt --upgrade pip

rabbitmq:
	docker run -d -p 5672:5672 --name "rabbitmq" rabbitmq

rabbitmq-start:
	docker start rabbitmq

celery:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && celery -A som.worker.celery worker --loglevel=INFO --pool=prefork --concurrency=4

celery-debian:
	celery -A som.worker.celery worker --loglevel=INFO --uid $(shell id -u nobody)  --pool=prefork --concurrency=2

celery-rabbitmq:
	make rabbitmq
	sleep 8
	make celery

style:
	isort som && black som
	pre-commit run --all-files

api-reload:
	uvicorn som.api.main:app --reload

api:
	uvicorn som.api.main:app --host 0.0.0.0 --port 8000

build-tag:
	docker build -t self-organizing-map

build:
	ENV_FILE=.env.docker.local docker compose build

docker-build-local:
	ENV_FILE=.env.docker.local docker compose up --build

docker-up-local:
	APP_PORT=8000 ENV_FILE=.env.docker.local docker compose up

docker-down:
	ENV_FILE=.env.docker.local docker compose down

docker-down-prod:
	ENV_FILE=.env.docker.prod docker-compose down

docker-build-prod:
	APP_PORT=80 ENV_FILE=.env.docker.prod docker-compose up --build

deploy-image:
	# todo: implement
	docker build .

login-registry:
	# todo: fix, invalid credential error
	aws ecr get-login-password --region eu-west-1 \
	| docker login --username AWS --password-stdin 544503054130.dkr.ecr.eu-west-1.amazonaws.com
