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

# Create a semantic version release (Requires GH_TOKEN to be set in the environment, with appropriate permissions)
.PHONY: release
release:
	# Tags are deleted from local env for better changelog file creation
	cd "$(ROOT_DIR)" \
	&& git tag -l '*dev*' | xargs git tag -d \
	&& semantic-release version \
	&& cd "$(EXEC_DIR)"

# Create a semantic version release for dev environment (Requires GH_TOKEN to be set in the environment, with appropriate permissions)
.PHONY: release_dev
release_dev:
	cd "$(ROOT_DIR)" \
	&& semantic-release version --no-changelog --no-vcs-release \
	&& cd "$(EXEC_DIR)"

.PHONY: format
format:
	cd "$(ROOT_DIR)" \
	&& uv run ruff check --select I,RUF022,F401 --fix --exit-zero \
	&& uv run ruff format . \
	&& cd "$(EXEC_DIR)"
	#&& uv run nbstripout notebooks/*.ipynb \

.PHONY: lint
lint:
	cd "$(ROOT_DIR)" \
	&& uvx --with tox-uv --python 3.11 tox -e lint \
	&& cd "$(EXEC_DIR)"

dump_config_to_yaml:  ## Generate a YAML config file from current configuration
	PYTHONPATH=src uv run python -c "from config.helpers.config_exporter import dump_config_to_yaml; dump_config_to_yaml('config_dump.yaml')"

dump_config_to_dotenv:  ## Generate a YAML config file from current configuration
	PYTHONPATH=src uv run python -c "from config.helpers.config_exporter import dump_config_to_dotenv; dump_config_to_dotenv()"