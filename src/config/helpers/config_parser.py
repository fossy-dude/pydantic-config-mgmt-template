"""
Helper functions to read a YAML config file.

Basically trims the functionality offered by pydantic_yaml to just return the parsed dict object
Source - https://github.com/NowanIlfideme/pydantic-yaml/blob/df903563ced25e26f43aa6a2e760cd370ae49dea/src/pydantic_yaml/loader.py # noqa
"""

from io import BytesIO, IOBase, StringIO
from pathlib import Path
from typing import TextIO, Union

from pydantic import validate_call
from ruamel.yaml import YAML


def parse_yaml_raw_as_dict(raw: str | bytes | IOBase | TextIO) -> dict:
    """
    Parse raw YAML string as a dict object.

    Parameters
    ----------
    raw : Union[str, bytes, IOBase, TextIO]
        The YAML string or stream to parse.

    Returns
    -------
    dict
        Parsed YAML content as a dictionary.

    Raises
    ------
    TypeError
        If input is not str, bytes, or IOBase type.

    Notes
    -----
    Supports YAML 1.2 specification using ruamel.yaml with safe loading.
    Input can be a string, bytes, or any IO stream object.
    """
    stream: IOBase
    if isinstance(raw, str):
        stream = StringIO(raw)
    elif isinstance(raw, bytes):
        stream = BytesIO(raw)
    elif isinstance(raw, IOBase):
        stream = raw
    else:
        raise TypeError(f"Expected str, bytes or IO, but got {raw!r}")
    reader = YAML(typ="safe", pure=True)  # YAML 1.2 support
    objects = reader.load(stream)

    return objects


@validate_call(config={"arbitrary_types_allowed": True})
def parse_yaml_file_as_dict(file: Path | str | IOBase) -> dict:
    """
    Parse YAML file as a dictionary.

    Parameters
    ----------
    file : Union[Path, str, IOBase]
        The file path or stream to read from. Can be a Path object,
        string path, or IO stream.

    Returns
    -------
    dict
        Parsed YAML file content as a dictionary.

    Raises
    ------
    TypeError
        If file parameter is not Path, str, or IOBase type.

    Notes
    -----
    If a string path is provided, it will be converted to a resolved Path object.
    The function handles both file paths and IO streams uniformly.
    """
    # Short-circuit for IO streams
    if isinstance(file, IOBase):
        return parse_yaml_raw_as_dict(raw=file)
    if isinstance(file, str):
        file = Path(file).resolve()
    elif isinstance(file, Path):
        file = file.resolve()
    else:
        raise TypeError(f"Expected Path, str or IO, but got {file!r}")

    with file.open(mode="r") as f:
        return parse_yaml_raw_as_dict(f)
