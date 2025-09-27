.PHONY: help install install-test run test test-all coverage lint format dump_config_to_yaml

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies using uv
	uv sync

install-all:  ## Install all optional dependencies (dev & test)
	uv sync --all-extras

run:  ## Run the main application
	python src/main.py

test:  ## Run tests with pytest (current Python version)
	pytest tests/ -v

test-all:  ## Run tests across all Python versions with tox
	tox

coverage:  ## Run tests with coverage report
	tox -e coverage

.PHONY: lint
lint:
	cd "$(ROOT_DIR)" \
	&& uvx --with tox-uv --python 3.12 tox -e lint \
	&& cd "$(EXEC_DIR)"

.PHONY: format
format:
	cd "$(ROOT_DIR)" \
	&& uv run ruff check --select I,RUF022 --fix \
	&& uv run ruff format . \
	&& cd "$(EXEC_DIR)"

dump_config_to_yaml:  ## Generate a YAML config file from current configuration
	PYTHONPATH=src uv run python -c "from config.helpers.config_exporter import dump_config_to_yaml; dump_config_to_yaml('config_dump.yaml')"

dump_config_to_dotenv:  ## Generate a YAML config file from current configuration
	PYTHONPATH=src uv run python -c "from config.helpers.config_exporter import dump_config_to_dotenv; dump_config_to_dotenv()"