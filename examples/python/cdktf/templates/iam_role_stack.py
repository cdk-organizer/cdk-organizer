import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.iam_role import IamRole, IamRoleInlinePolicy

if TYPE_CHECKING:
    from constructs import Construct
    from cdk_organizer.terraform.stack_group import StackGroup
    from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket

from cdk_organizer.terraform.stack import Stack


@dataclass
class IamRoleStackParameters:
    bucket: "S3Bucket"
    account_id: str


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

        AwsProvider(
            self,
            'Aws',
            region=self.config.get('region'),
        )

        IamRole(
            self,
            'Role',
            name=self.get_resource_name('role'),
            assume_role_policy=json.dumps({
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'sts:AssumeRole',
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': f'arn:aws:iam::{parameters.account_id}:root'
                        }
                    }
                ]
            }),
            inline_policy=[
                IamRoleInlinePolicy(
                    name='S3Access',
                    policy=json.dumps({
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Action': [
                                    's3:GetBucket*',
                                    's3:GetObject*',
                                    's3:List*'
                                ],
                                'Effect': 'Allow',
                                'Resource': [
                                    parameters.bucket.arn,
                                    f'{parameters.bucket.arn}/*'
                                ]
                            }
                        ]
                    })
                )
            ]
        )
