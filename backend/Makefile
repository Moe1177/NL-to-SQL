.ONESHELL:
SHELL=/bin/bash
PYTHON_VERSION=3.11.8
ENV_NAME="fastapi_backend"
ENV_DISPLAY_NAME="fastapi_backend"


datalink:
	ln -s PATH SHORTCUT


env:
	pyenv install --skip-existing $(PYTHON_VERSION)
	@if [ -z "$(env_exists)" ]; then \
		pyenv virtualenv $(PYTHON_VERSION) $(ENV_NAME); \
	fi
	pyenv local $(ENV_NAME)
	@eval "$$(pyenv init -)"
	@eval "$$(pyenv virtualenv-init -)"
	pip install --upgrade pip
	pip install poetry==1.8.5
	poetry config virtualenvs.create true
	poetry install --with dev


update-lock:
	poetry lock

update-env:
	poetry install --no-root --all-extras --with dev,test,code-quality,notebook

install:
	sudo apt-get update
	xargs -a packages.txt sudo apt-get install -y


clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf `find . -type d -name *.egg-info`
	rm -rf .coverage
