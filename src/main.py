"""Demonstrates usage of pydantic env variables."""

from config import get_config

if __name__ == "__main__":
    config = get_config()
    print("Printing loaded config...")
    print(config.model_dump_json(indent=4))
