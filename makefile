install:
	pip install -r requirements.txt

rabbitmq:
	docker run -d -p 5672:5672 rabbitmq

celery:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && celery -A som.tasks worker --loglevel=INFO

celery-debian:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && celery -A som.tasks worker --loglevel=INFO --uid $(id -u nobody);

celery-rabbitmq:
	make rabbitmq
	sleep 8
	make celery

style:
	isort som && black som
	pre-commit run --all-files

api-reload:
	uvicorn som.main:app --reload

api:
	uvicorn som.main:app
