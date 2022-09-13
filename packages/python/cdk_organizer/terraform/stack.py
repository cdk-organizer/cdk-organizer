"""CDK Infra Core Terraform Base Stack."""

from typing import TYPE_CHECKING

from cdktf import S3Backend, TerraformStack

if TYPE_CHECKING:
    from constructs import Construct
    from cdk_organizer.aws.stack_group import StackGroup

from cdk_organizer.decorators.catch_exceptions import catch_exceptions
from cdk_organizer.stack import BaseStack


class Stack(BaseStack, TerraformStack):
    """
    Base class for Terraform CDK Stacks.

    The Terraform Backend is configured to the S3 Bucket and DynamoDB table.

    The S3 Bucket stores the Terraform state files and the DynamoDB table locks the state when it is in use.

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
        TerraformStack.__init__(self, scope, id, **kwargs)

        backend_config = stack_group.config.get('s3_backend', None)
        if backend_config:
            self.backend_base_args = backend_config
            S3Backend(
                self,
                key=f'{id}/terraform.tfstate',
                **self.backend_base_args,
            )
