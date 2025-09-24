from pathlib import Path

PROJECT_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def get_project_basedir() -> Path:
    """
    Get the project base directory path.

    Returns
    -------
    Path
        The absolute path to the project's root directory,
        calculated relative to this file's location.

    Notes
    -----
    This function returns a Path object pointing to the project root,
    which is four levels up from this helper file's location:
    project_root/src/config/helpers/get_project_basedir.py -> project_root/
    """
    return PROJECT_BASE_DIR
