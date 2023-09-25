"""Include YAML tag constructor."""

import json
import os
from typing import IO, Any

import yaml


def custom_compose_document(self):
    """Override the default compose_document method, and removes the `self.anchors = {}` line."""
    self.get_event()
    node = self.compose_node(None, None)
    self.get_event()
    return node


yaml.SafeLoader.compose_document = custom_compose_document


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
                included_loader = yaml_path_loader(filename)(f.read())
                included_loader.anchors = loader.anchors

                return included_loader.get_data()
            elif extension in ('json', ):
                return json.load(f)
            else:
                return f.read()

    yaml.add_constructor('!include', construct_include, Loader)
    return Loader
