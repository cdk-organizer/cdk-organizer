"""S3 Bucket Stack."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket

if TYPE_CHECKING:
    from constructs import Construct
    from cdk_organizer.terraform.stack_group import StackGroup

from cdk_organizer.terraform.stack import Stack


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

        AwsProvider(
            self,
            'Aws',
            region=self.config.get('region'),
        )

        self.bucket = S3Bucket(
            self,
            'S3Bucket',
            bucket=self.get_bucket_name(parameters.base_bucket_name)
        )
