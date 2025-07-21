import os
import yaml
from typing import Any, Dict

class ConfigLoader:
    """
    Loads and validates YAML configuration files, with support for environment variable overrides.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.isfile(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config or {}

    def get(self, key: str, default: Any = None) -> Any:
        # Environment variable override (e.g., FFMPEG_AUDIO_CODEC)
        env_key = key.upper().replace('.', '_')
        if env_key in os.environ:
            return os.environ[env_key]
        # Nested key support (e.g., 'ffmpeg.audio_codec')
        parts = key.split('.')
        value = self.config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value 