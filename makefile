install:
	pip install -r requirements.txt

rabbitmq:
	docker run -d -p 5672:5672 rabbitmq

celery:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && celery -A som.tasks worker --loglevel=INFO --pool=prefork --concurrency=4

celery-debian:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && celery -A som.tasks worker --loglevel=INFO --uid $(id -u nobody)  --pool=prefork --concurrency=2

celery-rabbitmq:
	make rabbitmq
	sleep 8
	make celery

style:
	isort som && black som
	pre-commit run --all-files

api-reload:
	uvicorn som.main:fastapi --reload

api:
	uvicorn som.main:fastapi --host 0.0.0.0 --port 8000

build:
	docker compose build
