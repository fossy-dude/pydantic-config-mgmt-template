from __future__ import annotations as _annotations  # important for BaseSettings import to work

import json
import os
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import boto3
from pydantic_settings import EnvSettingsSource
from pydantic_settings.sources.utils import parse_env_vars

if TYPE_CHECKING:
    from pydantic_settings.main import BaseSettings


boto3_client = None
SecretsManagerClient = None


def _get_aws_credentials() -> dict[str, Any]:
    """
    Get AWS credentials from config, preferring access keys over profile.

    Important: A similarly named function is defined in utils.s3. Use that for all use-cases. It needs to be redefined
    here because this module is used to BUILD the pydantic configuration. get_config() is not built till this runs successfully.
    As a result, os.environ is used to source values for different variables.
    """
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")
    AWS_PROFILE = os.environ.get("AWS_PROFILE")

    if AWS_ACCESS_KEY_ID is not None and AWS_SECRET_ACCESS_KEY is not None:
        return {
            "aws_access_key_id": AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
            "region_name": AWS_DEFAULT_REGION,
        }
    elif AWS_PROFILE is not None:
        return {
            "profile_name": AWS_PROFILE,
            "region_name": AWS_DEFAULT_REGION,
        }
    else:
        # Let AWS library figure out the configuration
        return {"region_name": AWS_DEFAULT_REGION}


def get_aws_secret(secret_id: str) -> str:
    """Return the secret from AWS as a string for a given secret id."""
    client = boto3.Session(**_get_aws_credentials()).client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_id)
    return response["SecretString"]


class AWSSecretsManagerSettingsSource(EnvSettingsSource):
    _secret_id: str
    _secretsmanager_client: SecretsManagerClient  # type: ignore

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        secret_id: str,
        case_sensitive: bool | None = True,
        env_prefix: str | None = None,
        env_nested_delimiter: str | None = "--",
        env_parse_none_str: str | None = None,
        env_parse_enums: bool | None = None,
    ) -> None:
        self._secret_id = secret_id
        super().__init__(
            settings_cls,
            case_sensitive=case_sensitive,
            env_prefix=env_prefix,
            env_nested_delimiter=env_nested_delimiter,
            env_ignore_empty=False,
            env_parse_none_str=env_parse_none_str,
            env_parse_enums=env_parse_enums,
        )

    def _load_env_vars(self) -> Mapping[str, str | None]:
        # type: ignore
        secret = get_aws_secret(secret_id=self._secret_id)
        parsed_secret = json.loads(secret)
        return parse_env_vars(
            parsed_secret,
            self.case_sensitive,
            self.env_ignore_empty,
            self.env_parse_none_str,
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(secret_id={self._secret_id!r}, "
            f"env_nested_delimiter={self.env_nested_delimiter!r})"
        )


__all__ = [
    "AWSSecretsManagerSettingsSource",
]
