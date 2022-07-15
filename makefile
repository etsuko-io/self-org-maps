install:
	pip install -r requirements.txt

rabbitmq:
	docker run -d -p 5672:5672 rabbitmq

celery:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && celery -A tasks worker --loglevel=INFO

style:
	isort . && black .
