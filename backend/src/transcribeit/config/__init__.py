from .environment import EnvVarConfig
from ..helpers.singleton import singleton

@singleton
class AppConfig:
    def __init__(self):
        self.env: EnvVarConfig = EnvVarConfig()

def get_config() -> AppConfig:
    return AppConfig()