from pydantic import Field

from config.models.aws import AWSConfig
from config.helpers.base import BaseConfigModel
from config.models.db import DBConfig
from config.models.logging import LoggingConfig
from config.models.lookup_files import LookupDataConfig


class AppConfig(BaseConfigModel):
    """
    Main application configuration model that consolidates all configuration sections.

    Attributes
    ----------
    SERVICE_NAME : str
        Name of the service, defaults to "my_service_name".
    DB : DBConfig
        Database configuration including connection details and performance settings.
    AWS_CONFIG : AWSConfig
        AWS-related configuration including S3 buckets and CloudWatch settings.
    LLM : LLMConfig
        Language model configuration including API keys and model parameters.
    LOOKUP_DATA : LookupDataConfig
        File path configurations with validation for required lookup files.

    Notes
    -----
    This class inherits from BaseConfigModel, which provides configuration source
    priority handling (secrets > env vars > dotenv > YAML > defaults) and
    nested environment variable support using "__" delimiter.
    """

    SERVICE_NAME: str = "my_service_name"
    DB: DBConfig = Field(default_factory=DBConfig)
    AWS_CONFIG: AWSConfig = Field(default_factory=AWSConfig)
    LOOKUP_DATA: LookupDataConfig = Field(default_factory=LookupDataConfig)
    LOGGING: LoggingConfig = Field(default_factory=LoggingConfig)
