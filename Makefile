MODEL_PATH := $(shell pwd)/models

.PHONY: deploy destroy write_env

deploy: write_env
	docker-compose up -d --build

destroy:
	docker-compose down --volumes --rmi all
	docker rmi -f $(shell docker images -a -q)
	sudo rm -rf $(MODEL_PATH)

write_env:
	@echo MODEL_PATH=$(MODEL_PATH) > .env
