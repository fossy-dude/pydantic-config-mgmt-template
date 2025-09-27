from typing import Annotated

from pydantic import BaseModel, Field, SecretStr


class DBPerfConfig(BaseModel):
    """
    Database performance and connection pool configuration.

    Attributes
    ----------
    POOL_SIZE : int
        Total number of connections in the connection pool, defaults to 20.
    WEB_CONCURRENCY : int
        Number of web workers for concurrent processing, defaults to 5.
    """

    POOL_SIZE: Annotated[int, Field(description="Total number of connections in the pool")] = 20
    WEB_CONCURRENCY: Annotated[int, Field(description="Number of web workers")] = 5


class DBConfig(BaseModel):
    """
    Database connection and authentication configuration.

    Attributes
    ----------
    DB_NAME : str
        Name of the database to connect to, defaults to "DBNAME".
    SCHEMA_NAMES : str
        Schema used for core service operations (requires R/W permissions), defaults to "SCHEMA".
    USERNAME : SecretStr
        Database username, stored securely and masked in dumps.
    PASSWORD : SecretStr
        Database password, stored securely and masked in dumps.
    HOST : str
        Database host address, defaults to "127.0.0.1".
    PORT : int
        Database port number, defaults to 5432.
    PERF : DBPerfConfig
        Database performance and connection pool configuration.
    """

    DB_NAME: str = "DBNAME"
    SCHEMA_NAMES: Annotated[
        str,
        Field(description="Schema used for core service (R/W permissions reqd)"),
    ] = "SCHEMA"
    USERNAME: SecretStr = SecretStr("DB_USERNAME")
    PASSWORD: SecretStr = SecretStr("DB_PASS")
    HOST: str = "127.0.0.1"
    PORT: int = 5432
    PERF: DBPerfConfig = Field(default_factory=DBPerfConfig)
