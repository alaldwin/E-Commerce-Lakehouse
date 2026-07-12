from pathlib import Path
import yaml


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml_config(file_name: str) -> dict:
    """
    Load a YAML config file from the project / config folder.
    Example:
        load_yaml_config("paths.yaml")
        load_yaml_config("tables.yaml")
    """
    config_path = get_project_root() / "config" / file_name

    print(f"Loading config from: {config_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)