def convert_str_config_to_bool(value: str, none_as_false: bool = True) -> bool:
    if value is None:
        return none_as_false
    elif isinstance(value, (int, bool)):
        return bool(value)
    elif isinstance(value, str):
        return False if (value.lower() in ("false", "0", "no", "n", "f")) else True
