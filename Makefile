# Variables
PYTHON=python
PIP=pip
PROJECT_NAME=bitbucket-issues
APP_NAME=app
MODULE=api
ENV_PATH=venv

# Commands
.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: run
run:
	$(PYTHON) -m $(APP_NAME) $(MODULE)

.PHONY: test
test:
	pytest

.PHONY: format
format:
	black $(APP_NAME) tests

.PHONY: lint
lint:
	flake8 $(APP_NAME) tests

.PHONY: clean
clean:
	rm -rf $(ENV_PATH)
	find . -name "*.pyc" -type f -delete
	find . -name "__pycache__" -type d -delete

.PHONY: setup
setup:
	$(PYTHON) -m venv $(ENV_PATH)
	source $(ENV_PATH)/bin/activate && $(PIP) install --upgrade pip
	source $(ENV_PATH)/bin/activate && $(PIP) install -r requirements.txt
	source $(ENV_PATH)/bin/activate && $(PIP) install -r requirements-dev.txt

.PHONY: build
build:
	docker build -f ./package/Dockerfile -t $(PROJECT_NAME) .

.PHONY: docker-run
docker-run:
	docker run --name $(PROJECT_NAME) --rm -p 8000:8000 $(PROJECT_NAME)
