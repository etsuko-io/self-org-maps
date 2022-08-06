install:
	pip install -r requirements.txt

rabbitmq:
	docker run -d -p 5672:5672 --name "rabbitmq" rabbitmq

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

build:
	docker compose build

docker-build-local:
	ENV_FILE=.env.docker.local docker compose up --build

docker-up-local:
	ENV_FILE=.env.docker.local docker compose up

docker-down:
	ENV_FILE=.env.docker.local docker compose down

docker-build-prod:
	ENV_FILE=.env.docker.prod docker compose up --build
