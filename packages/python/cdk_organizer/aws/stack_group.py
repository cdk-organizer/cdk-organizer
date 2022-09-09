"""AWS CDK Stack Group Class."""

from typing import TypeVar

from aws_cdk import App
from cdk_organizer.stack_group import StackGroup as BaseStackGroup
from cdk_organizer.stack_group import StackGroupLoader

CDK_CONFIG_TYPE = TypeVar('CDK_CONFIG_TYPE', covariant=True)


class StackGroup(BaseStackGroup[App, CDK_CONFIG_TYPE]):
    """Stack Group for AWS CDK."""

    def __init__(self, app: App, loader: StackGroupLoader) -> None:
        """Stack group constructor."""
        super().__init__(app, loader)
