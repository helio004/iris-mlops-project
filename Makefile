MODEL_PATH := $(shell pwd)/models

.PHONY: deploy destroy clean_models clean_images write_env

deploy: write_env
	docker-compose up -d --build

destroy: clean_images clean_models
	docker rmi -f $(shell docker images -a -q)
	docker-compose down --volumes --rmi all
	sudo rm -rf $(MODEL_PATH)

write_env:
	@echo MODEL_PATH=$(MODEL_PATH) > .env
