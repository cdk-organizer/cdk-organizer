"""
Config Loader.

All the config files are located in the `config` folder and must match with the stacks folder.

### Example:

If stack group is located at `stacks.cloe.cdc.stacks` the config file \
    must be at `config/<env>/<region>/cloe/cdc/config.yaml`.

The files are also loaded recursively and all the propertires are merged together.

### Example:

Consider the following config structure:

```text
.
+-- config/
| +-- config.yaml (`prop1: value1`)
| +-- dev/
|   +-- config.yaml (`prop2: value2`)
|   +-- us-east-/
|       +-- config.yaml (`prop3: value3`)
|       +-- app1/
|           +-- config.yaml (`prop4: value4`)
```

The config object for the `dev/us-east-/app1` stack will be:

```yaml
prop1: value1
prop2: value2
prop3: value3
prop4: value4
```

> **Note**: If the property name conflicts, the higher priority config file will \
    override the lower priority config file.

"""

import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Tuple, TypeVar

import yaml
from constructs import IConstruct

CDK_APP_TYPE = TypeVar('CDK_APP_TYPE', bound=IConstruct)


class ConfigLoader(object):
    """Configuration Loader from YAML file to dict object based on the CDK Stack Groups."""

    def __init__(self, app: CDK_APP_TYPE, env: str, region: str) -> None:
        """
        Initialize the Configuration Loader.

        Args:
            app (CDK_APP_TYPE): CDK App instance
            env (str): environment name
            region (str): region name
        """
        super().__init__()

        self.app = app
        self.env = env
        self.region = region
        self._stack_dir = app.node.try_get_context("stacksDirectory") or "stacks"
        self._config_dir = app.node.try_get_context("configDirectory") or "config"

    def merge_dict(self, dict1: dict, dict2: dict, path=None) -> dict:
        """
        Merge two dict objects.

        Args:
            dict1 (dict): first dict object
            dict2 (dict): second dict object
            path (list): dict property path
        Returns:
            dict merged dict object
        """
        if path is None:
            path = []
        for key in dict2:
            if key in dict1:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    self.merge_dict(dict1[key], dict2[key], path + [str(key)])
                elif dict1[key] == dict2[key]:
                    pass  # same leaf value
                else:
                    dict1[key] = dict2[key]
            else:
                dict1[key] = dict2[key]
        return dict1

    def _load_config_recursive(self, path: Path, config: dict = {}) -> dict:
        if not path.exists():
            return self._load_config_recursive(path.parent, config)
        else:
            for filename in os.listdir(path):
                if fnmatch(filename, "*.yaml"):
                    with open(os.path.join(path, filename), 'r') as file:
                        file_data = yaml.safe_load(file.read())

                    config = self.merge_dict(file_data or {}, config)

            if str(path) != ".":
                config = self._load_config_recursive(path.parent, config)

            return config

    def load_config(self, module: str) -> Tuple[dict, bool]:
        """
        Load the configuration from the YAML file to the dict object.

        Args:
            module (str): module name

        Returns:
            configuration object and if the module config exists.
        """
        module_path = Path(module.replace(".", "/"))
        module_folder = module_path
        ignore_parts = self._stack_dir.count("/") + 1
        if not module_path.is_dir():
            module_folder = module_path.parent
        module_folder = Path(f'{self._config_dir}/{self.env}/{self.region}').joinpath(Path(*module_folder.parts[ignore_parts:]))
        module_config = module_folder.joinpath("config.yaml")

        config = self._load_config_recursive(module_folder)

        return config, module_config.exists()
