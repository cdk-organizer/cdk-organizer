import { Stack, StackGroup } from '@awslv/cdktf-organizer';
import { Construct } from 'constructs';
import { IamRole } from '@cdktf/provider-aws/lib/iam';
import { S3Bucket } from '@cdktf/provider-aws/lib/s3';
import { AwsProvider } from "@cdktf/provider-aws";

export type RoleStackProps = {
  bucket: S3Bucket;
  accountId: string;
};

export class RoleStack extends Stack {
  constructor(
    stackGroup: StackGroup,
    scope: Construct,
    id: string,
    props: RoleStackProps
  ) {
    super(stackGroup, scope, id);

    new AwsProvider(this, 'Aws', {
      region: this.config['region'] as string,
    })

    new IamRole(this, 'Role', {
      assumeRolePolicy: JSON.stringify({
        Version: '2012-10-17',
        Statement: [
          {
            Action: 'sts:AssumeRole',
            Effect: 'Allow',
            Principal: {
              AWS: `arn:aws:iam::${props.accountId}:root`,
            },
          },
        ],
      }),
      inlinePolicy: [
        {
          name: 'S3Access',
          policy: JSON.stringify({
            Version: '2012-10-17',
            Statement: [
              {
                Action: ['s3:GetBucket*', 's3:GetObject*', 's3:List*'],
                Effect: 'Allow',
                Resource: [
                  props.bucket.arn,
                  `${props.bucket.arn}/*`,
                ],
              },
            ],
          }),
        },
      ],
      name: this.getResourceName('role'),
    });
  }
}
