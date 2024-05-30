DATA_PATH := $(pwd)/models
DATA_PATH := $(shell pwd)/models

.PHONY: deploy destroy

deploy:
	docker-compose up -d --build

destroy:
	docker-compose down --volumes --rmi all
	docker rmi -f $(shell docker images -a -q)
	sudo rm -rf models
