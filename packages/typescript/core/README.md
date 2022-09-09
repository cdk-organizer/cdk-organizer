# CDK Organizer TypeScript Library

This library contains the core features to handle CDK projects including:

- Configuration Resolver
- Stack Groups Loader
- Naming Utils

## Project Structure

To apply the pattern purposed in this library for CDK projects, the following structure is required:

```text
.
+-- cdk.json
+-- bin/main.ts
```

### Stack Structure

the stack class needs to inherit from class `import { Stack } from '@awslv/aws-cdk-organizer'` for AWS CDK and `import { Stack } from '@awslv/cdkft-organizer'` for Terraform CDK.

#### AWS CDK

```typescript
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
```

#### Terraform CDK

```typescript
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
```

#### Using S3 Backend

To use S3 terraform backend, the following resources are required:

- S3 Bucket
- DynamoDB Table

Modify the `cdktf.json` to add the following object:

```json
{
  ...
  "context": {
    ...
    "s3Backend": {
      "bucket": "<bucket-name>",
      "region": "<aws-region>",
      "dynamodbTable": "<dynamodb-table-name>"
    }
    ...
  }
  ...
}
```

### Stack Group Structure

Create a `stacks` folder in the root of the project and structure it as follows:

```text
.
+-- cdk.json
+-- bin/main.ts
+-- stacks/
| +-- <groupName>/
|   +-- stacks.ts
```

The stack groups files follow this pattern:

#### AWS CDK

```typescript
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
```

#### Terraform

```typescript
import { StackGroup } from '@awslv/cdktf-organizer';
import { BaseConfig } from '@awslv/cdk-organizer-core';
import { S3Bucket } from '@cdktf/provider-aws/lib/s3';
import { S3Stack } from '../../templates/s3-stack';

type StorageStackGroupProps = {
  bucketName: string;
} & BaseConfig;

export class StorageStackGroup extends StackGroup<StorageStackGroupProps> {
  public bucket!: S3Bucket;

  override async loadStacks(): Promise<void> {
    this.bucket = new S3Stack(this, this.app, this.getStackName('bucket'), {
      bucketName: this.data.bucketName,
    }).bucket;
  }
}
```

#### Using Stack Attributes from Other Stack Groups

In some cases, you may want to use the attributes of another stack group. For example, refer the DNS Hosted Zone created by a shared stack group.

To resolve the group use the `this.resolveGroup` function in the stack group class, like the example below:

```typescript
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
```

The function `getStackName` generates the stack name based on following pattern.

**Pattern**: `{module_path}-{name}-{region}-{env}`

Consider the following example:

**module_path**: `myproject.myapp.www`
**name**: `spa`
**region**: `us-east-1`
**env**: `dev`

Stack name will be:

- `myproject-myapp-www-spa-us-east-1-dev`.

### Config Structure

Create a `config` folder in the root of the project and structure it as follows:

```text
.
+-- cdk.json
+-- bin/main.ts
+-- config/
| +-- <env>/
|   +-- config.yaml
|   +-- <region>/
|     +-- config.yaml
|     +-- <groupName>/
|         +-- config.yaml
```

The first two levels are reserved to the environment name and the region name, the next levels needs to match the stack group structure.

Example:

```text
.
+-- cdk.json
+-- bin/main.ts
+-- config/
| +-- config.yaml
| +-- dev/
|   +-- config.yaml
|   +-- us-east-1/
|     +-- config.yaml
|     +-- app1/
|       +-- config.yaml
+-- stacks/
| +-- app1/
|   +-- stacks.ts
+-- templates/
|   +-- stacks/
```

### Examples

- [AWS CDK](https://github.com/lucasvieirasilva/cdk-organizer/tree/main/examples/typescript/aws-cdk)
- [CDK for Terraform](https://github.com/lucasvieirasilva/cdk-organizer/tree/main/examples/typescript/cdktf)
