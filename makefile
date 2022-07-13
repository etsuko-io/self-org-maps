install:
	pip install -r requirements.txt

rabbitmq:
	docker run -d -p 5672:5672 rabbitmq

celery:
	celery -A tasks worker --loglevel=INFO

style:
	isort . && black .
