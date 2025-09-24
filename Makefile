.PHONY: help install install-test run test test-all coverage lint format dump_config_to_yaml

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies using uv
	uv sync

install-test:  ## Install dependencies including test dependencies
	uv sync --extra test

run:  ## Run the main application
	python src/main.py

test:  ## Run tests with pytest (current Python version)
	pytest tests/ -v

test-all:  ## Run tests across all Python versions with tox
	tox

coverage:  ## Run tests with coverage report
	tox -e coverage

lint:  ## Run linting checks
	tox -e lint

format:  ## Format code with ruff
	ruff format .

dump_config_to_yaml:  ## Generate a YAML config file from current configuration
	PYTHONPATH=src uv run python -c "from config.helpers.config_exporter import dump_config_to_yaml; dump_config_to_yaml('config_dump.yaml')"

dump_config_to_dotenv:  ## Generate a YAML config file from current configuration
	PYTHONPATH=src uv run python -c "from config.helpers.config_exporter import dump_config_to_dotenv; dump_config_to_dotenv()"