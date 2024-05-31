MODEL_PATH := $(shell pwd)/models
ENV_FILE=.env

.PHONY: deploy destroy write_env

up: write_env
	docker-compose up -d --build

down:
	docker-compose down --volumes --rmi all
	docker rmi -f $(shell docker images -a -q)
	rm -f $(ENV_FILE)
	sudo rm -rf $(MODEL_PATH)

write_env:
	@echo MODEL_PATH=$(MODEL_PATH) > $(ENV_FILE)
