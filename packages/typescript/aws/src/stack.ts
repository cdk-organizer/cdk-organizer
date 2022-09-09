import { BaseStack, StackGroup } from '@awslv/cdk-organizer-core';
import { Stack as AwsStack, StackProps, Tags } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as _ from 'lodash';

export class Stack<TStackProps extends StackProps> extends AwsStack {
  private base: BaseStack;
  public config: Record<string, unknown>;
  public env: string;
  getResourceName: typeof StackGroup.prototype.getResourceName;
  getBucketName: typeof BaseStack.prototype.getBucketName;

  constructor(
    stackGroup: StackGroup,
    scope?: Construct,
    id?: string,
    props?: TStackProps
  ) {
    super(scope, id, {
      ...props,
      env: {
        account: stackGroup.data.account,
        region: stackGroup.data.region,
      },
    });

    this.base = new BaseStack(stackGroup);
    this.config = stackGroup.config;
    this.env = stackGroup.env;

    this.getResourceName = this.base.getResourceName.bind(this.base);
    this.getBucketName = this.base.getBucketName.bind(this.base);

    Tags.of(this).add('Environment', this.base.config['env'] as string);
    if (!_.isNil(this.base.config['tags'])) {
      Object.entries(
        this.base.config['tags'] as Record<string, string>
      ).forEach(([key, value]) => {
        Tags.of(this).add(key, value);
      });
    }
  }
}
