from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, SecretStr, model_validator


class AWSConfig(BaseModel):
    """AWS configuration for authentication and service access."""

    AWS_PROFILE: Optional[str] = Field(
        default=None,
        description="AWS CLI profile name to use for authentication",
        validation_alias=AliasChoices("AWS__AWS_PROFILE", "AWS_PROFILE"),
    )
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = Field(
        default=None,
        description="AWS access key ID for authentication",
        validation_alias=AliasChoices("AWS__AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID"),
    )
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = Field(
        default=None,
        description="AWS secret access key for authentication",
        validation_alias=AliasChoices("AWS__AWS_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY"),
    )
    AWS_DEFAULT_REGION: str = Field(default="us-east-1", description="AWS region for service operations")

    @model_validator(mode="after")
    def validate_auth_config(self) -> "AWSConfig":
        """Validate that either AWS_PROFILE or access keys are provided."""
        has_profile = self.AWS_PROFILE is not None
        has_access_keys = self.AWS_ACCESS_KEY_ID is not None and self.AWS_SECRET_ACCESS_KEY is not None

        if not has_profile and not has_access_keys:
            raise ValueError("Either AWS_PROFILE or both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be provided")

        return self

    def use_profile_auth(self) -> bool:
        """Check if profile-based authentication should be used."""
        return self.AWS_PROFILE is not None

    def use_key_auth(self) -> bool:
        """Check if access key-based authentication should be used."""
        return self.AWS_ACCESS_KEY_ID is not None and self.AWS_SECRET_ACCESS_KEY is not None
