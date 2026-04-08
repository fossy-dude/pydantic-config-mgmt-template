# Shortcuts for project testing and development using Just
# On windows, install `just` by running `uv tool install rust-just`

# Set shell based on operating system
# Windows uses PowerShell, Mac/Linux use bash
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set shell := ["bash", "-cu"]

# Base directory - Location of this file
ROOT_DIR := justfile_directory()

# Directory from which the script is being executed
EXEC_DIR := invocation_directory()

export PYTHONPATH := "src"

# Default recipe to display help
default:
    @just --list

# Run app on port 8002, with reload on code update
dump_config_to_yaml:  ## Generate a YAML config file from current configuration
	uv run python -c "from config.helpers.config_exporter import dump_config_to_yaml; dump_config_to_yaml('config_dump.yaml')"

dump_config_to_dotenv:  ## Generate a YAML config file from current configuration
	uv run python -c "from config.helpers.config_exporter import dump_config_to_dotenv; dump_config_to_dotenv('.env.dump',exclude_unset=True)"

dump_config_to_json:  ## Generate a YAML config file from current configuration
    uv run python -c "from config.helpers.config_exporter import dump_config_to_json; dump_config_to_json('config_dump.json',exclude_unset=True,include_plain_secret_values=True,in_aws_format=True)"

# Run tox checks
test:
    cd "{{ROOT_DIR}}"
    uvx --with tox-uv --python 3.13 tox
    cd "{{EXEC_DIR}}"

# Run pytest via tox
pytest:
    cd "{{ROOT_DIR}}"
    uvx --with tox-uv --python 3.13 tox -e pytest_all
    cd "{{EXEC_DIR}}"

# Format code with ruff
format:
    cd "{{ROOT_DIR}}"
    uv run ruff check --select I,RUF022,F401 --fix --exit-zero
    uv run ruff format .
    cd "{{EXEC_DIR}}"

# Run linting checks
lint:
    cd "{{ROOT_DIR}}"
    just format
    uvx --with tox-uv --python 3.13 tox -e lint
    cd "{{EXEC_DIR}}"