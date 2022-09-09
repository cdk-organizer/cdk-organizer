from cdk_organizer.aws.stack_group import StackGroup
from stacks.config import EnvironmentStackGroupConfig
from stacks.storage.stacks import StorageStackGroup
from templates.iam_role_stack import IamRoleStack, IamRoleStackParameters


class IamStackGroup(StackGroup[EnvironmentStackGroupConfig]):
    def _load_stacks(self) -> None:
        IamRoleStack(
            self.app,
            self.get_stack_name("role"),
            stack_group=self,
            parameters=IamRoleStackParameters(
                bucket=self.resolve_group(StorageStackGroup).bucket
            )
        )
