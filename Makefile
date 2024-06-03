MODEL_PATH := $(shell pwd)/models
ENV_FILE := .env
DOT_DOCKER := .docker

.PHONY: deploy destroy write_env

up: write_env
	docker-compose up -d --build

down:
	docker-compose down --volumes --rmi all
	docker rmi -f $(shell docker images -a -q)
	rm -f $(ENV_FILE)
	rm -rf $(DOT_DOCKER)
	sudo rm -rf $(MODEL_PATH)

write_env:
	@echo MODEL_PATH=$(MODEL_PATH) > $(ENV_FILE)
