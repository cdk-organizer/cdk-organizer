"""S3 Bucket Stack."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aws_cdk import CfnOutput
from aws_cdk.aws_s3 import Bucket

if TYPE_CHECKING:
    from constructs import Construct
    from cdk_organizer.aws.stack_group import StackGroup

from cdk_organizer.aws.stack import Stack


@dataclass
class S3BucketStackParameters:
    base_bucket_name: str


class S3BucketStack(Stack):
    def __init__(
        self,
        scope: "Construct",
        id: str,
        stack_group: "StackGroup",
        parameters: S3BucketStackParameters,
        **kwargs
    ) -> None:
        super().__init__(scope, id, stack_group, **kwargs)

        self.bucket = Bucket(
            self,
            'S3Bucket',
            bucket_name=self.get_bucket_name(parameters.base_bucket_name)
        )

        CfnOutput(self, 'BucketName', value=self.bucket.bucket_name)
        CfnOutput(self, 'BucketArn', value=self.bucket.bucket_arn)
