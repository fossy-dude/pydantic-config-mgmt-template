# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Pydantic configuration template project demonstrating best practices for managing application configuration in Python. The project showcases how to use Pydantic Settings to handle configuration from multiple sources (environment variables, .env files, secrets, YAML files) with type validation and nested configuration models.

## Development Commands

- **Install dependencies**: `uv sync` (requires uv package manager)
- **Install test dependencies**: `make install-test` or `uv sync --extra test`
- **Run the demo**: `python src/main.py` 
- **Run tests**: `make test` or `pytest tests/ -v`
- **Run tests across Python versions**: `make test-all` or `tox`
- **Run tests with coverage**: `make coverage` or `tox -e coverage`
- **Run linting**: `make lint` or `tox -e lint`
- **Format code**: `make format` or `tox -e format`
- **Generate config YAML**: `make dump_config_to_yaml`
- **Activate virtual environment**: After `uv sync`, activate the created virtual environment

## Architecture

The configuration system is built around a layered architecture:

### Core Components

- `src/config/models/consolidated.py`: Main `AppConfig` class that aggregates all configuration models
- `src/config/helpers/base.py`: `BaseConfigModel` providing shared configuration settings and source priority
- `src/config/__init__.py`: Configuration factory with `get_config()` function (cached)

### Configuration Models (src/config/models/)
- `aws.py`: AWS-related configuration (S3 buckets, etc.)
- `db.py`: Database connection settings
- `llm.py`: Language model configuration
- `lookup_files.py`: File path configurations with validation

### Configuration Sources Priority (Highest to Lowest)
1. Docker secrets (`/run/secrets`)
2. Environment variables
3. `.env` files
4. `config.yaml` file (optional)
5. Default values in models

### Key Features

- **Nested Configuration**: Uses `__` delimiter for nested env vars (e.g., `DB__HOST`)
- **Path Validation**: Custom validators (`RequiredFile`, `RequiredFolder`) ensure files/directories exist
- **Type Safety**: Full Pydantic type validation with custom types
- **Multiple Sources**: Supports env vars, .env files, secrets, and YAML
- **Caching**: Configuration is cached using `@functools.lru_cache`

## Configuration Usage

1. Import: `from config import get_config`
2. Get config: `config = get_config()`
3. Access nested values: `config.DB.HOST` or `config.AWS_CONFIG.S3_BUCKET_NAMES.BUCKET_A`

## Testing

The project includes comprehensive tests covering:

- **Configuration generation**: Tests that config loads without errors and has required sections
- **Precedence validation**: Tests the priority chain (secrets > env vars > dotenv > defaults)  
- **Sensitive data protection**: Tests that `SecretStr` fields are masked in dumps and YAML exports
- **YAML export functionality**: Tests the `dump_config_to_yaml()` function

### Test Commands

- **Quick tests**: `make test` (current Python version only)
- **Full test suite**: `make test-all` (tests across Python 3.11, 3.12 using tox)
- **Coverage report**: `make coverage` (generates HTML and terminal coverage reports)
- **Linting**: `make lint` (runs ruff and mypy checks). WHen a user asks you to run linter, run this and fix all issues
- **Code formatting**: `make format` (formats code with ruff)

Test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`. Test files are in the `tests/` directory.

## Testing Configuration

Create a `.env` file based on `.env.example` to test environment variable sourcing. For YAML configuration, create a `config.yaml` file in the project root.

## Code Standards

### Package Management
   - ONLY use uv, NEVER pip
   - Installation: `uv add package`
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`, `@latest` syntax

### Code Quality

- Functions must be focused and small
- Always write tests for any core business logic. Ensure all edge cases are covered. Present the user with the list of scenarios and ask for inputs to refine this before writing code
- Testing:
  - Use pytest for all unit, integration and functional tests
  - Create separate directories inside the tests folder for `unit`, `integration`, and `functional` tests. Each folder has its own data in a `data` subdirectory, fixtures, factories for generating dummy data (using `faker` and `factory-boy` packages)
- Follow SOLID principles wherever possible:
  - Single Responsibility Principle: Each class should have only one purpose. It should not try to multitask any more than it has to. It's not to say each class can only have one function.
  - Open Closed Principle: When you write a class or function or library you should do it in a way that anyone else can easily build on to it, but not change it's core elements.
  - Liskov's Substitution Principle: Any time you have a sub-type of something, that subtype should be 100% compatible with the original thing. This is usually not an issue since a subtype is a specialized version of the more generic thing.
  - Dependency Inversion Principle: High level modules shouldn't depend on low level modules, both should depend on abstractions. For example, database calls should be made in business logic layers via adapters and not direct calls. Same for Any network or AWS api calls
- PEP 8 naming (snake_case for functions/variables)
  - Class names in PascalCase
  - Constants in UPPER_SNAKE_CASE
  - Document with docstrings
  - Use f-strings for formatting
- Add tags like "# FIXME", "# TODO" to mark issues or areas requiring interventions
- Folder structure: Follow industry best practices
  - `src` is the project's source code directory. Should be top level. All source code should be placed within it
  - `tests` is the directory for all tests. Should be in the root directory
  - Helpers (non-core logic) should be inside separate files/folders called helpers
  - Common utilities should all be placed in the utilities package
  - Use pydantic for all user configuration. THe configurations are grouped and placed within `src/config/models`. Update this whenever new configuration needs to be added

### Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand. Add short comments explaining why a chunk of code exists. Don't go above 120 characters in a line
- **Performance**: Consider performance without sacrificing readability
- **Secure**: Ensure all common CVEs and security issues are addressed
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint. Use DRY principles (Don't duplicate code)

### Type Hints
- **MANDATORY**: All functions, methods, and class attributes MUST have complete type annotations
- Use `typing` module imports for complex types (Union, Optional, etc.). Prefer simple types like dict,str over typing module's types
- Return types are required for all functions and methods
- Use `Union[str, Path]` instead of `str | Path` for Python 3.8+ compatibility
- Example:
  ```python
  from typing import Optional, Dict, Union
  from pathlib import Path
  
  def load_config(filename: str = "config.yaml") -> Optional[Dict[str, Any]]:
      pass
  ```

### Docstrings  
- **MANDATORY**: All public functions, methods, and classes MUST have docstrings in NumPy format
- Private methods need not have this
- Include comprehensive parameter descriptions with types
- Document return values and exceptions
- Add Notes section for important implementation details
- Example:
  ```python
  def parse_yaml_file(file: Union[Path, str]) -> Dict[str, Any]:
      """
      Parse YAML file as a dictionary.

      Parameters
      ----------
      file : Union[Path, str]
          The file path to read from. Can be a Path object or string path.

      Returns
      -------
      Dict[str, Any]
          Parsed YAML file content as a dictionary.

      Raises
      ------
      TypeError
          If file parameter is not Path or str type.

      Notes
      -----
      If a string path is provided, it will be converted to a resolved Path object.
      """
  ```

### Validation
- Run `make lint` before committing to ensure type hints and code quality
- Use mypy for static type checking
- All type hints must pass mypy validation without errors

### Git Conventions

This project uses Conventional Commits for commit messages. All commits must follow the format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Common Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples
- `feat: add YAML configuration export functionality`
- `fix: resolve environment variable precedence issue`
- `docs: update configuration usage examples`
- `test: add tests for sensitive data masking`