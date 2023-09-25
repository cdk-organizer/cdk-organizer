"""Include YAML tag constructor."""

import json
import os
from typing import IO, Any

import yaml


def yaml_path_loader(path: str) -> yaml.SafeLoader:
    """
    YAML Path Loader.

    Example:

    `a.yaml`

    ```yaml
    b: !include b.yaml
    ```

    `b.yaml`

    ```yaml
    key: value
    ```

    Args:
        path (str): YAML file path

    Returns:
        yaml.SafeLoader: YAML Loader
    """
    class Loader(yaml.SafeLoader):
        def __init__(self, stream: IO) -> None:
            self._root = os.path.dirname(path)
            super().__init__(stream)

    def construct_include(loader: Loader, node: yaml.Node) -> Any:
        filename = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
        extension = os.path.splitext(filename)[1].lstrip('.')

        with open(filename, 'r') as f:
            if extension in ('yaml', 'yml'):
                return yaml.load(f, Loader)
            elif extension in ('json', ):
                return json.load(f)
            else:
                return f.read()

    yaml.add_constructor('!include', construct_include, Loader)
    return Loader
