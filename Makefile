DATA_PATH := $(shell pwd)/models

.PHONY: deploy destroy

deploy:
	docker-compose up -d --build

destroy:
	docker-compose down --volumes --rmi all
	docker rmi -f $(shell docker images -a -q)
	sudo rm -rf models

predict:
	curl -d '{"instances": [{"sepal_length": 1.0, "sepal_width": 2.0, "petal_length": 2.0, "petal_width": 3.0}]}' \
		-X POST http://localhost:8501/v1/models/iris:predict
