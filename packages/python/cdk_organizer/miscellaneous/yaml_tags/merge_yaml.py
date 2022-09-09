"""Merge YAML tag constructor."""

from typing import Any, List

import yaml


def construct_merge(loader: yaml.SafeLoader, node: yaml.Node) -> List[Any]:
    """
    YAML !merge tag constructor.

    This tag is used to merge arrays
    Example:
        YAML file:
        ```yaml
        a: !merge
        - 1
        - 2
        - - 3
        - 4
        ```
        Output:
        ```json
        {
            "a": [
                1,
                2,
                3,
                4
            ]
        }
        ```

    Args:
        loader (Loader): YAML custom loader instance
        node (yaml.nodes.SequenceNode): YAML node
    Returns:
        A merge list of items
    """
    if not isinstance(node, yaml.nodes.SequenceNode):
        raise yaml.constructor.ConstructorError(
            None, None, f'expected a sequence node, but found {node.id}', node.start_mark)

    values = loader.construct_sequence(node)

    result = []
    for value in values:
        if isinstance(value, list):
            result += value
        else:
            result.append(value)

    return result
