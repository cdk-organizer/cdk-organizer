import { Stack } from '@awslv/aws-cdk-organizer';
import { StackGroup } from '@awslv/aws-cdk-organizer';
import { StackProps } from 'aws-cdk-lib';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export type S3StackProps = StackProps & {
  bucketName: string;
};

export class S3Stack extends Stack<S3StackProps> {
  public bucket: Bucket;

  constructor(
    stackGroup: StackGroup,
    scope: Construct,
    id: string,
    props: S3StackProps
  ) {
    super(stackGroup, scope, id, props);

    this.bucket = new Bucket(this, 'Bucket', {
      bucketName: this.getBucketName(props.bucketName)
    });
  }
}
