import { BaseStack, StackGroup } from '@awslv/cdk-organizer-core';
import { TerraformStack, S3Backend, S3BackendConfig } from 'cdktf';
import { Construct } from 'constructs';

export class Stack extends TerraformStack {
  private base: BaseStack;
  public config: Record<string, unknown>;
  public env: string;

  getResourceName: typeof StackGroup.prototype.getResourceName;
  getBucketName: typeof BaseStack.prototype.getBucketName;

  constructor(public stackGroup: StackGroup, scope: Construct, id: string) {
    super(scope, id);

    this.base = new BaseStack(stackGroup);
    this.config = stackGroup.config;
    this.env = stackGroup.env;

    this.getResourceName = this.base.getResourceName.bind(this.base);
    this.getBucketName = this.base.getBucketName.bind(this.base);

    const backendConfig = this.config['s3Backend'] as
      | S3BackendConfig
      | undefined;
    if (backendConfig) {
      new S3Backend(this, { ...backendConfig });
    }
  }
}
