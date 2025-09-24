from pydantic import BaseModel, Field

from config.helpers.base import RequiredFile


class LookupDataConfig(BaseModel):
    """
    Configuration for required lookup files with path validation.

    Attributes
    ----------
    DATA_FILE_1 : RequiredFile
        Path to a required data file, defaults to "pyproject.toml".
        The file existence is validated at configuration load time.

    Notes
    -----
    Uses the RequiredFile custom type which validates that the file exists
    and returns a Path object. Paths can be absolute, relative to the project
    base directory, or include user home directory references (~).
    """

    DATA_FILE_1: RequiredFile = Field("pyproject.toml", description="Path to a required data file.")
