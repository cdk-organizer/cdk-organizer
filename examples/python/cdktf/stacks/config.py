from dataclasses import dataclass


@dataclass
class EnvironmentStackGroupConfig:
    env: str
    account: str
    region: str
    short_region: str
