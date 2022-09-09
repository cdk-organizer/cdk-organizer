import { StackGroup } from '@awslv/aws-cdk-organizer';
import { BaseConfig } from '@awslv/cdk-organizer-core';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { S3Stack } from '../../templates/s3-stack';

type StorageStackGroupProps = {
  bucketName: string;
} & BaseConfig;

export class StorageStackGroup extends StackGroup<StorageStackGroupProps> {
  public bucket!: Bucket;

  override async loadStacks(): Promise<void> {
    this.bucket = new S3Stack(this, this.app, this.getStackName('bucket'), {
      bucketName: this.data.bucketName,
    }).bucket;
  }
}
