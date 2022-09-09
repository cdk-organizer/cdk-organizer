import { StackGroup } from '@awslv/aws-cdk-organizer';
import { RoleStack } from '../../templates/role-stack';
import { StorageStackGroup } from '../storage/stacks';

export class IamStackGroup extends StackGroup {
  override async loadStacks(): Promise<void> {
    const storageGroup = await this.resolveGroup(StorageStackGroup);

    new RoleStack(this, this.app, this.getStackName('role'), {
      bucket: storageGroup.bucket,
    });
  }
}
