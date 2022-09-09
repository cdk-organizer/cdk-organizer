from dataclasses import dataclass

from cdk_organizer.aws.stack_group import StackGroup
from stacks.config import EnvironmentStackGroupConfig
from templates.s3_stack import S3BucketStack, S3BucketStackParameters


@dataclass
class StorageStackGroupConfig(EnvironmentStackGroupConfig):
    bucket_name: str


class StorageStackGroup(StackGroup[StorageStackGroupConfig]):
    def _load_stacks(self) -> None:
        self.bucket = S3BucketStack(
            self.app,
            self.get_stack_name("bucket"),
            stack_group=self,
            parameters=S3BucketStackParameters(
                base_bucket_name=self.data.bucket_name
            )
        ).bucket
