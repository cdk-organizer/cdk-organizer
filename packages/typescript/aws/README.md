# CDK Organizer for AWS CDK TypeScript Library

This library contains the core features to handle CDK projects including:

- Configuration Resolver
- Stack Groups Loader
- Naming Utils

Full documentation: <https://cdk-organizer.github.io/>

## Installation

```bash
npm install --save @awslv/aws-cdk-organizer
```

## Project Structure

To apply the pattern purposed in this library for CDK projects, the following structure is required:

```text
.
+-- cdk.json
+-- bin/main.ts
```

### CDK Start Script

The content of the `bin/main.ts` file should be as follows:

```typescript
#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { StackGroupLoader } from "@awslv/cdk-organizer-core";

const app = new cdk.App();
const loader = new StackGroupLoader(app)

loader.synth().then(() => console.log("Stack Groups Synthesized"));
```

### Stack Structure

the stack class needs to inherit from class `import { Stack } from '@awslv/aws-cdk-organizer'` for AWS CDK.

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

> If you are using `typescript` version <4.3 you need to remove the `override` keyword.

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

> If you are using `typescript` version <4.3 you need to remove the `override` keyword.

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
