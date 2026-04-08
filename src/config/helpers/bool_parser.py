# pyrefly: ignore  # bad-return
def convert_str_config_to_bool(value: str, none_as_false: bool = True) -> bool:
    """
    Convert a configuration value to a boolean.

    Parameters
    ----------
    value : str
        The value to convert. Accepts strings like "false", "0", "no", "n", "f"
        (case-insensitive) as False; anything else as True.
    none_as_false : bool, optional
        If True, treat None values as False (default is True).

    Returns
    -------
    bool
        The converted boolean value.
    """
    if value is None:
        return none_as_false
    elif isinstance(value, (int, bool)):
        return bool(value)
    elif isinstance(value, str):
        return False if (value.lower() in ("false", "0", "no", "n", "f")) else True
