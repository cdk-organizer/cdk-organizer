"""CDK Infra Core AWS Base Stack."""

from typing import TYPE_CHECKING

import aws_cdk as cdk

if TYPE_CHECKING:
    from constructs import Construct
    from cdk_organizer.aws.stack_group import StackGroup

from cdk_organizer.decorators.catch_exceptions import catch_exceptions
from cdk_organizer.stack import BaseStack


class Stack(BaseStack, cdk.Stack):
    """
    Base class for AWS CDK Stacks.

    Args:
        scope (Construct): AWS CDK Construct object
        id (str): Stack Id
        stack_group (StackGroup): StackGroup instance
    """

    @catch_exceptions
    def __init__(
        self,
        scope: "Construct",
        id: str,
        stack_group: "StackGroup",
        **kwargs
    ) -> None:
        """Initialize the class."""
        BaseStack.__init__(self, id, stack_group)
        cdk.Stack.__init__(self, scope, id, env=self.env_props, **kwargs)

        cdk.Tags.of(self).add('Environment', self.env_name.upper())
        if 'tags' in self.config:
            for key, value in self.config['tags'].items():
                cdk.Tags.of(self).add(key, value)

        self.node.add_metadata('cdk:module', self.stack_group.module_name)
