"""Include YAML tag constructor."""

import glob
import json
import os
import pathlib
from typing import IO, Any

import yaml
from jinja2 import BaseLoader, Environment, StrictUndefined, UndefinedError


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

    There also can be a `params` key in the `!include` tag:

    ```yaml
    b: !include
      path: b.yaml
      params:
        key: value
    ```

    `b.yaml`
    ```yaml
    key: {{ key }}
    ```

    The variable `key` will be resolved to `value`, and the output will be:

    ```json
    {
        "b": {
            "key": "value"
        }
    }
    ```

    **NOTE**: The variables are resolved using Jinja2.

    Args:
        path (str): YAML file path

    Returns:
        yaml.SafeLoader: YAML Loader
    """
    class Loader(yaml.SafeLoader):
        def __init__(self, stream: IO) -> None:
            self._root = os.path.dirname(path)
            super().__init__(stream)

    def construct_include_pattern(loader: Loader, node: yaml.Node) -> Any:
        params = {}
        pattern = None
        if isinstance(node.value, str):
            pattern = loader.construct_scalar(node)
        else:
            value = loader.construct_mapping(node, True)
            if 'pattern' not in value:
                raise yaml.constructor.ConstructorError(None, None, f'expected a pattern, but found {value}', node.start_mark)

            pattern = value['pattern']
            params = value.get('params', {})

        return [
            resolve_file_content(filename, loader, params)
            for filename in glob.glob(os.path.join(loader._root, pattern))
        ]

    def construct_include(loader: Loader, node: yaml.Node) -> Any:
        params = {}
        path = None
        if isinstance(node.value, str):
            path = loader.construct_scalar(node)
        else:
            value = loader.construct_mapping(node, True)
            if 'path' not in value:
                raise yaml.constructor.ConstructorError(None, None, f'expected a path, but found {value}', node.start_mark)

            path = value['path']
            params = value.get('params', {})

        filename = os.path.abspath(os.path.join(loader._root, path))
        return resolve_file_content(filename, loader, params)

    yaml.add_constructor('!include', construct_include, Loader)
    yaml.add_constructor('!include_pattern', construct_include_pattern, Loader)
    return Loader


def resolve_variables(value: str, variables: dict) -> str:
    """
    Resolve Variables using Jinja2.

    Args:
        value (str): Value to be resolved
        variables (dict): Variables

    Returns:
        str: Resolved value
    """
    try:
        value_template = Environment(
            loader=BaseLoader,
            undefined=StrictUndefined,
            autoescape=True
        ).from_string(value)
        return value_template.render(variables)
    except UndefinedError as error:
        raise yaml.constructor.ConstructorError(None, None, f'undefined variable: {error}', None)


def resolve_file_content(path: str, loader: yaml.Loader, params: dict = {}) -> Any:
    """
    Resolve file content.

    Args:
        path (str): File path
        loader (yaml.Loader): YAML Loader
        params (dict, optional): Variables. Defaults to {}.

    Returns:
        Any: File content
    """
    extension = get_extension(path)

    with open(path, 'r') as f:
        if extension in ('yaml', 'yml'):
            included_loader = yaml_path_loader(path)(resolve_variables(f.read(), params))
            included_loader.anchors = loader.anchors

            return included_loader.get_data()
        elif extension in ('json', ):
            return json.load(f)
        else:
            return f.read()


def get_extension(path: str) -> str:
    """
    Get file extension.

    Args:
        path (str): File path

    Returns:
        str: File extension
    """
    return pathlib.Path(path).suffix.lstrip('.').lower()
