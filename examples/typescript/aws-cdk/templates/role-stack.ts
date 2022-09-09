import { Stack } from '@awslv/aws-cdk-organizer';
import { StackGroup } from '@awslv/aws-cdk-organizer';
import { StackProps } from 'aws-cdk-lib';
import { Role, AccountRootPrincipal } from 'aws-cdk-lib/aws-iam';
import { IBucket } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export type RoleStackProps = StackProps & {
  bucket: IBucket;
};

export class RoleStack extends Stack<RoleStackProps> {
  constructor(
    stackGroup: StackGroup,
    scope: Construct,
    id: string,
    props: RoleStackProps
  ) {
    super(stackGroup, scope, id, props);

    const role = new Role(this, 'Role', {
      assumedBy: new AccountRootPrincipal(),
      roleName: this.getResourceName('role'),
    })
    props.bucket.grantRead(role)
  }
}
