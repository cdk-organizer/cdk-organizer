import { Stack, StackGroup } from '@awslv/cdktf-organizer';
import { AwsProvider } from '@cdktf/provider-aws';
import { S3Bucket } from '@cdktf/provider-aws/lib/s3';
import { Construct } from 'constructs';

export type S3StackProps = {
  bucketName: string;
};

export class S3Stack extends Stack {
  public bucket: S3Bucket;

  constructor(
    stackGroup: StackGroup,
    scope: Construct,
    id: string,
    props: S3StackProps
  ) {
    super(stackGroup, scope, id);

    new AwsProvider(this, 'Aws', {
      region: this.config['region'] as string,
    })

    this.bucket = new S3Bucket(this, 'Bucket', {
      bucket: this.getBucketName(props.bucketName)
    });
  }
}
