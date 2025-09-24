# Pydantic Configuration Template

A production-ready Python configuration management system built with Pydantic that demonstrates best practices for handling application configuration from multiple sources with type validation and environment-specific overrides.

## Why Use This Template?

Traditional configuration management often leads to:

This template solves the typical problems caused by lack of standardized configuration management by providing:
- **Type Safety**: Catch configuration errors at startup, not at runtime, using the Pydantic library
- **Multiple Sources**: Environment variables, .env files, secrets, and YAML
- **Environment Flexibility**: Easy overrides for development, staging, and production
- **Nested Configuration**: Organize complex settings hierarchically
- **Security**: Built-in support for secrets and sensitive data masking (using types like SecretStr) which are automagically masked during logging
- **Debugging**: Pythonic access patterns for config variables which work well with linters & tools like mypy

## Real-World Benefits

### Example: AWS Profile Management

**Production Setup** (using defaults):
```python
# Your production code works with sensible defaults for env variables (provided during pydantic class declaration)
config = get_config()
print(config.AWS_CONFIG.AWS_PROFILE)  # "default"

# AWS SDK automatically uses the default profile configured on your production server
s3_client = boto3.client('s3', 
                        profile_name=config.AWS_CONFIG.AWS_PROFILE)
```

**Local Development** (easy overrides):
```bash
# Override for local development without changing code
export AWS_CONFIG__AWS_PROFILE="dev-profile"
python src/main.py  # Now uses "dev-profile"

# Or use a .env file for team consistency
echo 'AWS_CONFIG__AWS_PROFILE="dev-profile"' > .env

# Or create a config.yaml file for readability
#AWS_CONFIG:
#    AWS_PROFILE: "dev-profile"
```



### Example: Database Configuration

**Nested configuration with intelligent defaults (Each nested element is separated by 2 underscores):**
```python
# Production uses environment variables
# DB__HOST=prod-db.company.com
# DB__PORT=5432

config = get_config()
db_url = f"postgresql://{config.DB.HOST}:{config.DB.PORT}/app"
```

**Local development override:**
```bash
# .env file for local development
DB__HOST=localhost
DB__PORT=5433
```

## Configuration Sources (Priority Order)

1. **Docker Secrets** (`/run/secrets`) - Highest priority, for production secrets
2. **Environment Variables** - Great for CI/CD and containerized deployments  
3. **`.env` files** - Perfect for local development and team consistency
4. **`config.yaml`** - Optional structured configuration
5. **Default Values** - Sensible defaults defined in models

What does this mean? If a variable is defined in both `.env` and `config.yaml`, the value in the higher priority source is preferred (`.env` in this case)

## Quick Start

### Prerequisites
Install [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)

### Installation & Demo

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run with defaults:**
   ```bash
   python src/main.py
   # Or run `make dump_config_to_yaml`
   ```
   You'll see default configuration values for all settings.

3. **Try environment-specific overrides:**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Run again to see overridden values
   python src/main.py
   ```

4. **Test different override methods:**
   ```bash
   # Environment variable override
   export SERVICE_NAME="MyDevService"
   python src/main.py
   ```

## Configuration Structure

Each configuration logical group is inherited from the Pydantic BaseModel. For example, this template uses the below config:

- **`AWSConfig`**: AWS services (S3, CloudWatch, profiles)  
- **`DatabaseConfig`**: Database connection settings
- **`LLMConfig`**: Language model configurations
- **`LookupFilesConfig`**: File and directory paths with validation


These are inherited by the **`AppConfig`** container (in `consolidated.py`) which can be consumed across the app using the `get_config` convenience function.

```python
from config import get_config

config = get_config()

# Access nested values
aws_profile = config.AWS_CONFIG.AWS_PROFILE
bucket_name = config.AWS_CONFIG.S3_BUCKET_NAMES.BUCKET_A
db_host = config.DB.HOST

# Configuration is cached and validated once at startup
```

### Environment Variable Naming

Use double underscores (`__`) for nested configuration:

```bash
# Top-level
SERVICE_NAME="MyApp"

# Nested: config.DB.HOST
DB__HOST="localhost"

# Double nested: config.AWS_CONFIG.S3_BUCKET_NAMES.BUCKET_A  
AWS_CONFIG__S3_BUCKET_NAMES__BUCKET_A="my-dev-bucket"
```

## Development Commands

- **Run demo**: `python src/main.py`
- **Export config**: `make dump_config_to_yaml`
- **Run tests**: `make test`