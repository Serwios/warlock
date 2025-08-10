import os
import yaml
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "..", "config.yaml")

def load_config() -> Dict[str, Any]:
    config_path = os.path.abspath(CONFIG_FILE)
    if not os.path.exists(config_path):
        return {"telegram": {"token": "", "chat_id": ""}, "alerts": []}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def save_config(config: Dict[str, Any]) -> None:
    config_path = os.path.abspath(CONFIG_FILE)
    with open(config_path, "w") as f:
        yaml.dump(config, f)
