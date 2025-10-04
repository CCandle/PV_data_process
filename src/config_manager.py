import os
import yaml

class ConfigManager:
    """配置管理类"""

    def __init__(self, config_file="config/data_config.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self):
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"配置文件 '{self.config_file}' 不存在")
        with open(self.config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print(f"已加载配置文件: {self.config_file}")
        return config

    def _validate_config(self):
        channels_config = self.config["channels_config"]
        raw_columns = [ch["source"] for ch in channels_config if isinstance(ch["source"], str)]
        self.frame_size = len(raw_columns) + 2
        self.header_idx = 0
        self.tail_idx = self.frame_size - 1

    def get_setting(self, key, default=None):
        return self.config["settings"].get(key, default)

    def get_draw_config(self, key, default=None):
        return self.config["draw_config"].get(key, default)

    def get_channels_config(self):
        return self.config["channels_config"]

    def get_column_groups(self):
        return self.config["draw_config"]["column_groups"]

    def parse_hex_value(self, hex_str):
        return int(hex_str, 16) if isinstance(hex_str, str) and hex_str.startswith("0x") else int(hex_str)
