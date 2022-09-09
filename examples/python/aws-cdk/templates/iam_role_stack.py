from dataclasses import dataclass
from typing import TYPE_CHECKING

from aws_cdk.aws_iam import AccountRootPrincipal, Role

if TYPE_CHECKING:
    from constructs import Construct
    from cdk_organizer.aws.stack_group import StackGroup
    from aws_cdk.aws_s3 import IBucket

from cdk_organizer.aws.stack import Stack


@dataclass
class IamRoleStackParameters:
    bucket: "IBucket"


class IamRoleStack(Stack):
    def __init__(
        self,
        scope: "Construct",
        id: str,
        stack_group: "StackGroup",
        parameters: IamRoleStackParameters,
        **kwargs
    ) -> None:
        super().__init__(scope, id, stack_group, **kwargs)

        role = Role(
            self,
            'Role',
            role_name=self.get_resource_name('role'),
            assumed_by=AccountRootPrincipal()
        )

        parameters.bucket.grant_read(role)
